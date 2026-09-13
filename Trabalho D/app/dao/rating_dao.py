from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Rating


class RatingDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, rating_id: int) -> Rating | None:
        return self.db.get(Rating, rating_id)

    def get_all(self) -> list[Rating]:
        return list(self.db.scalars(select(Rating)).all())

    def get_by_user(self, user_id: int) -> list[Rating]:
        return list(self.db.scalars(select(Rating).where(Rating.user_id == user_id)).all())

    def get_by_music(self, music_id: str) -> list[Rating]:
        return list(self.db.scalars(select(Rating).where(Rating.music_id == music_id)).all())

    def create(self, rating: Rating) -> Rating:
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def save(self, rating: Rating) -> Rating:
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def delete(self, rating: Rating) -> None:
        self.db.delete(rating)
        self.db.commit()