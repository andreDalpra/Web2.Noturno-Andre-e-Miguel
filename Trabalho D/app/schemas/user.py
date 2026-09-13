from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    nickname: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=4, max_length=100)


class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str

    model_config = {"from_attributes": True}