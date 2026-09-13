from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.services import UserService

router = APIRouter(tags=["Users"])


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create(data)


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return UserService(db).list()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService(db).get(user_id)