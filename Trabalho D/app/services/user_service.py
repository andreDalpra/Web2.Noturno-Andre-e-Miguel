from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dao import UserDAO
from app.models import User
from app.schemas import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.users = UserDAO(db)

    def create(self, data: UserCreate) -> User:
        if self.users.exists_by_nickname_or_email(data.nickname, data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nickname or email already registered")
        return self.users.create(User(**data.model_dump()))

    def get(self, user_id: int) -> User:
        user = self.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def list(self) -> list[User]:
        return self.users.get_all()

    def get_by_identifier(self, identifier: str) -> User | None:
        return self.users.get_by_identifier(identifier)