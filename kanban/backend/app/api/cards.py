from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, get_role, require_board
from ..database import get_db
from ..models import Card, Column, User
from ..schemas.card import CardCreate, CardMove, CardOut, CardUpdate
from ..services import audit_service, card_service

router = APIRouter(tags=["cards"])


def _card_out(card: Card) -> CardOut:
    return CardOut.model_validate({**card.__dict__, "assignee": card.assignee, "comments_count": len(card.comments)})


def _get_card_with_board(db: Session, card_id: int) -> tuple[Card, int]:
    card = db.get(Card, card_id)
    if card is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Карточка не найдена")
    column = db.get(Column, card.column_id)
    return card, column.board_id


@router.post("/boards/{board_id}/cards", response_model=CardOut, status_code=201)
def create_card(board_id: int, data: CardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_board(db, board_id, user, "writer")
    column = db.get(Column, data.column_id)
    if column is None or column.board_id != board_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Колонка не принадлежит этой доске")
    card = Card(
        column_id=data.column_id, title=data.title, description=data.description,
        position=card_service.next_position(db, data.column_id),
    )
    db.add(card)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="card", entity_id=None, action="create", payload={"title": data.title})
    db.commit()
    db.refresh(card)
    return _card_out(card)


@router.patch("/cards/{card_id}", response_model=CardOut)
def update_card(card_id: int, data: CardUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card, board_id = _get_card_with_board(db, card_id)
    require_board(db, board_id, user, "writer")
    card_service.check_version(card, data.version)
    changes = {}
    if data.title is not None:
        changes["title"] = [card.title, data.title]
        card.title = data.title
    if data.description is not None:
        changes["description"] = True
        card.description = data.description
    if data.clear_assignee:
        card.assignee_id = None
        changes["assignee"] = None
    elif data.assignee_id is not None:
        if get_role(db, board_id, data.assignee_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Исполнитель должен быть участником доски")
        card.assignee_id = data.assignee_id
        changes["assignee"] = data.assignee_id
    if data.clear_deadline:
        card.deadline = None
        changes["deadline"] = None
    elif data.deadline is not None:
        card.deadline = data.deadline
        changes["deadline"] = data.deadline.isoformat()
    card.version += 1
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="card", entity_id=card.id, action="update", payload=changes)
    db.commit()
    db.refresh(card)
    return _card_out(card)


@router.post("/cards/{card_id}/move", response_model=CardOut)
def move_card(card_id: int, data: CardMove, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card, board_id = _get_card_with_board(db, card_id)
    require_board(db, board_id, user, "writer")
    card = card_service.move_card(db, card, user, board_id, data.target_column_id, data.position, data.version)
    return _card_out(card)


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card, board_id = _get_card_with_board(db, card_id)
    require_board(db, board_id, user, "writer")
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="card", entity_id=card.id, action="delete", payload={"title": card.title})
    db.delete(card)
    db.commit()
