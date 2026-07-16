from datetime import datetime

from pydantic import BaseModel, Field

from .auth import UserOut
from .column import ColumnOut


class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class BoardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    version: int  # оптимистичная блокировка: клиент присылает известную ему версию


class MemberOut(BaseModel):
    user: UserOut
    role: str

    model_config = {"from_attributes": True}


class MemberAdd(BaseModel):
    login: str
    role: str = Field(pattern="^(reader|writer|owner)$")


class MemberUpdate(BaseModel):
    role: str = Field(pattern="^(reader|writer|owner)$")


class BoardListItem(BaseModel):
    id: int
    title: str
    role: str
    cards_total: int
    updated_at: datetime


class BoardOut(BaseModel):
    id: int
    title: str
    description: str | None
    owner_id: int
    version: int
    my_role: str
    members: list[MemberOut]
    columns: list[ColumnOut]
