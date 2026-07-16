from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ._types import PK, FK

BOARD_ROLES = ("reader", "writer", "owner")


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(PK, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(FK, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # оптимистичная блокировка
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    columns = relationship("Column", cascade="all, delete-orphan", order_by="Column.position", lazy="selectin")
    members = relationship("BoardMember", cascade="all, delete-orphan", lazy="selectin")


class BoardMember(Base):
    __tablename__ = "board_members"

    board_id: Mapped[int] = mapped_column(FK, ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(FK, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(Enum(*BOARD_ROLES, name="board_role"), nullable=False, default="reader")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", lazy="joined")
