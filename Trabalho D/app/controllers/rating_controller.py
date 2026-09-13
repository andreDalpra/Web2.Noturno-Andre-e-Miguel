from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import FeedRatingResponse, RatingCreate, RatingResponse, RatingUpdate
from app.services import RatingService

router = APIRouter(tags=["Ratings"])


@router.post("/ratings", response_model=RatingResponse, status_code=201)
def create_rating(data: RatingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RatingService(db).create(data, current_user.id)


@router.get("/ratings", response_model=list[RatingResponse])
def list_ratings(db: Session = Depends(get_db)):
    return RatingService(db).list()


@router.get("/ratings/{rating_id}", response_model=RatingResponse)
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    return RatingService(db).get(rating_id)


@router.get("/ratings/user/id/{user_id}", response_model=list[RatingResponse])
def get_ratings_by_user_id(user_id: int, db: Session = Depends(get_db)):
    return RatingService(db).by_user(user_id)


@router.get("/ratings/user/nickname/{nickname}", response_model=list[RatingResponse])
def get_ratings_by_nickname(nickname: str, db: Session = Depends(get_db)):
    service = RatingService(db)
    user = service.users.get_by_nickname(nickname)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.by_user(user.id)


@router.get("/ratings/music/{music_id}", response_model=list[RatingResponse])
def get_ratings_by_music(music_id: str, db: Session = Depends(get_db)):
    return RatingService(db).by_music(music_id)


@router.get("/feed", response_model=list[FeedRatingResponse])
def feed(db: Session = Depends(get_db)):
    rows = RatingService(db).list()
    return [{**RatingResponse.model_validate(rating).model_dump(), "nickname": rating.user.nickname} for rating in rows]


@router.put("/ratings/{rating_id}", response_model=RatingResponse)
def update_rating(rating_id: int, data: RatingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RatingService(db).update(rating_id, data, current_user.id)


@router.delete("/ratings/{rating_id}")
def delete_rating(rating_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RatingService(db).delete(rating_id, current_user.id)
    return {"message": "Rating deleted successfully"}