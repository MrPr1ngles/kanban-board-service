from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, require_board
from ..database import get_db
from ..models import Board, BoardMember, Card, Column, User
from ..schemas.board import BoardCreate, BoardListItem, BoardOut, BoardUpdate
from ..services import audit_service
from ..services.card_service import check_version

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=list[BoardListItem])
def list_boards(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # JOIN + LEFT JOIN + GROUP BY: доски пользователя с числом карточек
    rows = db.execute(
        select(Board.id, Board.title, BoardMember.role, func.count(Card.id), Board.updated_at)
        .join(BoardMember, (BoardMember.board_id == Board.id) & (BoardMember.user_id == user.id))
        .outerjoin(Column, Column.board_id == Board.id)
        .outerjoin(Card, Card.column_id == Column.id)
        .group_by(Board.id, Board.title, BoardMember.role, Board.updated_at)
        .order_by(Board.updated_at.desc())
    ).all()
    return [
        BoardListItem(id=r[0], title=r[1], role=r[2], cards_total=r[3], updated_at=r[4])
        for r in rows
    ]


def board_to_out(db: Session, board: Board, user: User) -> BoardOut:
    from ..core.permissions import get_role
    from ..schemas.card import CardOut
    from ..schemas.column import ColumnOut

    columns = []
    for col in board.columns:
        cards = [
            CardOut.model_validate({**c.__dict__, "assignee": c.assignee, "comments_count": len(c.comments)})
            for c in col.cards
        ]
        columns.append(ColumnOut(id=col.id, title=col.title, position=col.position, cards=cards))
    return BoardOut(
        id=board.id, title=board.title, description=board.description,
        owner_id=board.owner_id, version=board.version,
        my_role=get_role(db, board.id, user.id),
        members=board.members, columns=columns,
    )


@router.post("", response_model=BoardOut, status_code=201)
def create_board(data: BoardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = Board(title=data.title, description=data.description, owner_id=user.id)
    db.add(board)
    db.flush()
    db.add(BoardMember(board_id=board.id, user_id=user.id, role="owner"))
    audit_service.log(db, board_id=board.id, user_id=user.id, entity="board", entity_id=board.id, action="create", payload={"title": data.title})
    db.commit()
    db.refresh(board)
    return board_to_out(db, board, user)


@router.get("/{board_id}", response_model=BoardOut)
def get_board(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "reader")
    return board_to_out(db, board, user)


@router.patch("/{board_id}", response_model=BoardOut)
def update_board(board_id: int, data: BoardUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "writer")
    check_version(board, data.version)
    changes = {}
    if data.title is not None:
        changes["title"] = [board.title, data.title]
        board.title = data.title
    if data.description is not None:
        changes["description"] = True
        board.description = data.description
    board.version += 1
    audit_service.log(db, board_id=board.id, user_id=user.id, entity="board", entity_id=board.id, action="update", payload=changes)
    db.commit()
    db.refresh(board)
    return board_to_out(db, board, user)


@router.delete("/{board_id}", status_code=204)
def delete_board(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "owner")
    db.delete(board)
    db.commit()
