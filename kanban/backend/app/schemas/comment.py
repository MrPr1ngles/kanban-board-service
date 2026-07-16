from datetime import datetime

from pydantic import BaseModel, Field

from .auth import UserOut


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class CommentOut(BaseModel):
    id: int
    author: UserOut
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
