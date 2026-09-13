from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    music_id: str
    rating: float = Field(ge=0.5, le=5)
    description: str = Field(max_length=255)
    user_id: int | None = None


class RatingUpdate(BaseModel):
    rating: float = Field(ge=0.5, le=5)
    description: str = Field(max_length=255)


class RatingResponse(BaseModel):
    id: int
    user_id: int
    music_id: str
    rating: float
    description: str | None

    model_config = {"from_attributes": True}


class FeedRatingResponse(RatingResponse):
    nickname: str