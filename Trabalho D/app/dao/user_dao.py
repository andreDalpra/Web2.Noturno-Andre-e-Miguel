from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import User


class UserDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_nickname(self, nickname: str) -> User | None:
        return self.db.scalar(select(User).where(User.nickname == nickname))

    def get_by_identifier(self, identifier: str) -> User | None:
        return self.db.scalar(select(User).where(or_(User.email == identifier, User.nickname == identifier)))

    def get_all(self) -> list[User]:
        return list(self.db.scalars(select(User)).all())

    def exists_by_nickname_or_email(self, nickname: str, email: str) -> bool:
        return self.db.scalar(select(User).where(or_(User.nickname == nickname, User.email == email))) is not None

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user