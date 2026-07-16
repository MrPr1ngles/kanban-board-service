from datetime import datetime

from pydantic import BaseModel, Field

from .auth import UserOut


class CardCreate(BaseModel):
    column_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    clear_assignee: bool = False
    deadline: datetime | None = None
    clear_deadline: bool = False
    version: int


class CardMove(BaseModel):
    target_column_id: int
    position: float
    version: int


class CardOut(BaseModel):
    id: int
    column_id: int
    title: str
    description: str | None
    assignee: UserOut | None
    deadline: datetime | None
    position: float
    version: int
    comments_count: int = 0

    model_config = {"from_attributes": True}
