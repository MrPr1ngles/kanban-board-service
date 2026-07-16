from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, require_board
from ..database import get_db
from ..models import Column, User
from ..schemas.column import ColumnCreate, ColumnOut, ColumnUpdate
from ..services import audit_service

router = APIRouter(tags=["columns"])


@router.post("/boards/{board_id}/columns", response_model=ColumnOut, status_code=201)
def create_column(board_id: int, data: ColumnCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_board(db, board_id, user, "writer")
    max_pos = db.execute(select(func.max(Column.position)).where(Column.board_id == board_id)).scalar()
    col = Column(board_id=board_id, title=data.title, position=(max_pos or 0) + 1)
    db.add(col)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="column", entity_id=None, action="create", payload={"title": data.title})
    db.commit()
    db.refresh(col)
    return ColumnOut(id=col.id, title=col.title, position=col.position, cards=[])


def _get_column(db: Session, column_id: int) -> Column:
    col = db.get(Column, column_id)
    if col is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Колонка не найдена")
    return col


@router.patch("/columns/{column_id}", response_model=ColumnOut)
def update_column(column_id: int, data: ColumnUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    col = _get_column(db, column_id)
    require_board(db, col.board_id, user, "writer")
    if data.title is not None:
        col.title = data.title
    if data.position is not None:
        col.position = data.position
    audit_service.log(db, board_id=col.board_id, user_id=user.id, entity="column", entity_id=col.id, action="update", payload=data.model_dump(exclude_none=True))
    db.commit()
    db.refresh(col)
    from ..schemas.card import CardOut
    cards = [CardOut.model_validate({**c.__dict__, "assignee": c.assignee, "comments_count": len(c.comments)}) for c in col.cards]
    return ColumnOut(id=col.id, title=col.title, position=col.position, cards=cards)


@router.delete("/columns/{column_id}", status_code=204)
def delete_column(column_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    col = _get_column(db, column_id)
    require_board(db, col.board_id, user, "writer")
    audit_service.log(db, board_id=col.board_id, user_id=user.id, entity="column", entity_id=col.id, action="delete", payload={"title": col.title})
    db.delete(col)
    db.commit()
