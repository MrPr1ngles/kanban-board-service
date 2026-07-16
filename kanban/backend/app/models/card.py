from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ._types import PK, FK


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(PK, primary_key=True)
    column_id: Mapped[int] = mapped_column(FK, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    assignee_id: Mapped[int | None] = mapped_column(FK, ForeignKey("users.id", ondelete="SET NULL"))
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # fractional indexing: вставка между A и B -> (A+B)/2, без переиндексации колонки
    position: Mapped[float] = mapped_column(Numeric(20, 10), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    assignee = relationship("User", lazy="joined")
    comments = relationship("Comment", cascade="all, delete-orphan", order_by="Comment.created_at", lazy="selectin")
