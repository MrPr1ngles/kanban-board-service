from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Card, Column, User
from . import audit_service

POSITION_STEP = 1024.0  # шаг fractional indexing для новых карточек


def next_position(db: Session, column_id: int) -> float:
    last = (
        db.query(Card.position)
        .filter(Card.column_id == column_id)
        .order_by(Card.position.desc())
        .first()
    )
    return float(last[0]) + POSITION_STEP if last else POSITION_STEP


def check_version(entity, incoming_version: int) -> None:
    """Оптимистичная блокировка: конфликт версий -> 409, клиент перечитывает состояние."""
    if entity.version != incoming_version:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Объект был изменён другим пользователем. Обновите доску и повторите.",
        )


def move_card(db: Session, card: Card, user: User, board_id: int, target_column_id: int, position: float, version: int) -> Card:
    """Перемещение карточки: смена колонки + позиция + version + audit — одна транзакция."""
    check_version(card, version)
    target = db.get(Column, target_column_id)
    if target is None or target.board_id != board_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Целевая колонка не принадлежит этой доске")
    source_column_id = card.column_id
    card.column_id = target_column_id
    card.position = position
    card.version += 1
    audit_service.log(
        db, board_id=board_id, user_id=user.id, entity="card", entity_id=card.id, action="move",
        payload={"from_column": source_column_id, "to_column": target_column_id, "position": position},
    )
    db.commit()
    db.refresh(card)
    return card
