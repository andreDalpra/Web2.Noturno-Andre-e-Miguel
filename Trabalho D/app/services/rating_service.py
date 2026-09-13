from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao import RatingDAO, UserDAO
from app.models import Rating
from app.schemas import RatingCreate, RatingUpdate


class RatingService:
    def __init__(self, db: Session):
        self.ratings = RatingDAO(db)
        self.users = UserDAO(db)

    def list(self) -> list[Rating]:
        return self.ratings.get_all()

    def get(self, rating_id: int) -> Rating:
        rating = self.ratings.get_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        return rating

    def create(self, data: RatingCreate, user_id: int) -> Rating:
        if round(data.rating * 2) != data.rating * 2:
            raise HTTPException(status_code=422, detail="Rating must be in 0.5 increments")
        if not self.users.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return self.ratings.create(Rating(
            user_id=user_id, music_id=data.music_id, rating=data.rating, description=data.description
        ))

    def by_user(self, user_id: int) -> list[Rating]:
        return self.ratings.get_by_user(user_id)

    def by_music(self, music_id: str) -> list[Rating]:
        return self.ratings.get_by_music(music_id)

    def update(self, rating_id: int, data: RatingUpdate, user_id: int) -> Rating:
        rating = self.get(rating_id)
        if rating.user_id != user_id:
            raise HTTPException(status_code=403, detail="You can only edit your own ratings")
        if round(data.rating * 2) != data.rating * 2:
            raise HTTPException(status_code=422, detail="Rating must be in 0.5 increments")
        rating.rating, rating.description = data.rating, data.description
        return self.ratings.save(rating)

    def delete(self, rating_id: int, user_id: int) -> None:
        rating = self.get(rating_id)
        if rating.user_id != user_id:
            raise HTTPException(status_code=403, detail="You can only delete your own ratings")
        self.ratings.delete(rating)