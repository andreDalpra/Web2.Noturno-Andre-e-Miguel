from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    nickname: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=4, max_length=100)


class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str

    class Config:
        from_attributes = True


class AuthUserResponse(UserResponse):
    pass


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


class RatingCreate(BaseModel):
    # Kept optional only to preserve the old request format. The API ignores it
    # and always assigns the authenticated user to the new review.
    user_id: int | None = None
    music_id: str = Field(min_length=1, max_length=100)
    rating: float = Field(ge=0.5, le=5)
    description: str = Field(max_length=255)


class RatingUpdate(BaseModel):
    rating: float = Field(ge=0.5, le=5)
    description: str = Field(max_length=255)


class RatingResponse(BaseModel):
    id: int
    user_id: int
    music_id: str
    rating: float
    description: str

    class Config:
        from_attributes = True


class FeedRatingResponse(RatingResponse):
    nickname: str
