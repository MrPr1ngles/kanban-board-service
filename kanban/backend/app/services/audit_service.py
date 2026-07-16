from sqlalchemy.orm import Session

from ..models import AuditLog


def log(db: Session, *, board_id: int | None, user_id: int, entity: str, entity_id: int | None, action: str, payload: dict | None = None) -> None:
    """Запись в историю изменений. Коммитится вместе с основной операцией (одна транзакция)."""
    db.add(AuditLog(board_id=board_id, user_id=user_id, entity=entity, entity_id=entity_id, action=action, payload=payload))
