from pydantic import BaseModel


class UserCreate(BaseModel):
    nickname: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str
    password: str

    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    user_id: int
    music_id: str
    rating: float
    description: str

class RatingResponse(BaseModel):
    id: int
    user_id: int
    music_id: str
    rating: float
    description: str

    class Config:
        from_attributes = True