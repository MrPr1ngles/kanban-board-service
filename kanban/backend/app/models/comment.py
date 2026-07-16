from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ._types import PK, FK


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(PK, primary_key=True)
    card_id: Mapped[int] = mapped_column(FK, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(FK, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", lazy="joined")
