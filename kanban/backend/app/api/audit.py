from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, require_board
from ..database import get_db
from ..models import AuditLog, User

router = APIRouter(tags=["audit"])


@router.get("/boards/{board_id}/audit")
def board_audit(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_board(db, board_id, user, "owner")
    rows = db.execute(
        select(AuditLog).where(AuditLog.board_id == board_id).order_by(AuditLog.created_at.desc()).limit(100)
    ).scalars().all()
    return [
        {
            "id": r.id, "user": r.user.login if r.user else None, "entity": r.entity,
            "entity_id": r.entity_id, "action": r.action, "payload": r.payload,
            "created_at": r.created_at,
        }
        for r in rows
    ]
