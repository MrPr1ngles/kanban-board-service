from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ._types import PK, FK


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(PK, primary_key=True)
    board_id: Mapped[int | None] = mapped_column(FK, ForeignKey("boards.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(FK, ForeignKey("users.id", ondelete="SET NULL"))
    entity: Mapped[str] = mapped_column(String(32), nullable=False)   # board / column / card / comment / member
    entity_id: Mapped[int | None] = mapped_column(FK)
    action: Mapped[str] = mapped_column(String(32), nullable=False)   # create / update / delete / move
    payload: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", lazy="joined")
