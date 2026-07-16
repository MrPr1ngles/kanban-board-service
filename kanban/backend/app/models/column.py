from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ._types import PK, FK


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(PK, primary_key=True)
    board_id: Mapped[int] = mapped_column(FK, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    cards = relationship("Card", cascade="all, delete-orphan", order_by="Card.position", lazy="selectin")
