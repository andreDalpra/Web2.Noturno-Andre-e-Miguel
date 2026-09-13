from datetime import datetime

from pydantic import BaseModel, Field


class PlaylistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    collaborative: bool = False


class PlaylistUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    collaborative: bool


class ParticipantResponse(BaseModel):
    id: int
    nickname: str

    model_config = {"from_attributes": True}


class TrackCreate(BaseModel):
    spotify_id: str = Field(min_length=1, max_length=100)


class PlaylistResponse(BaseModel):
    id: int
    name: str
    collaborative: bool
    created_at: datetime
    participants: list[ParticipantResponse]
    spotify_ids: list[str]