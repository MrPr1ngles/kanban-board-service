from pydantic import BaseModel, Field


class Credentials(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class TokenOut(BaseModel):
    auth_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    login: str

    model_config = {"from_attributes": True}
