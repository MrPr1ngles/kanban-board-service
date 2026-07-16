from pydantic import BaseModel, Field

from .card import CardOut


class ColumnCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ColumnUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    position: int | None = None


class ColumnOut(BaseModel):
    id: int
    title: str
    position: int
    cards: list[CardOut]

    model_config = {"from_attributes": True}
