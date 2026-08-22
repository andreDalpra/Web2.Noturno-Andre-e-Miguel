from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from spotify import SpotifyAPI
from dotenv import load_dotenv
import models
import os
import schemas
import main
import schemas
load_dotenv()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
sp = SpotifyAPI(client_id=os.getenv("SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# CRUD operations for the user model
# Create user
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    new_user = models.User(
        nickname=user.nickname,
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
# List users
@app.get("/users", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):

    users = db.query(models.User).all()

    return users

# Get user by ID
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# Update user
@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    data: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.nickname = data.nickname
    user.email = data.email
    user.password = data.password

    db.commit()
    db.refresh(user)

    return user

# Delete user
@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }

# CRUD operations for the rating model
# Create rating
@app.post("/ratings", response_model=schemas.RatingResponse)
def create_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):

    new_rating = models.Rating(
        user_id=rating.user_id,
        music_id=rating.music_id,
        rating=rating.rating,
        description=rating.description
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating

# List ratings
@app.get("/ratings", response_model=list[schemas.RatingResponse])
def list_ratings(db: Session = Depends(get_db)):

    ratings = db.query(models.Rating).all()

    return ratings

# Get rating by ID
@app.get("/ratings/{rating_id}", response_model=schemas.RatingResponse)
def get_rating(rating_id: int, db: Session = Depends(get_db)):

    rating = (
        db.query(models.Rating)
        .filter(models.Rating.id == rating_id)
        .first()
    )

    if not rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found"
        )

    return rating

@app.get("/ratings/user/id/{user_id}", response_model=list[schemas.RatingResponse])
def get_ratings_by_userId(user_id: int, db: Session = Depends(get_db)):

    ratings = (
        db.query(models.Rating)
        .filter(models.Rating.user_id == user_id)
        .all()
    )

    if not ratings:
        raise HTTPException(
            status_code=404,
            detail="Ratings not found for the user"
        )

    return ratings

@app.get("/ratings/user/nickname/{nickname}", response_model=list[schemas.RatingResponse])
def get_ratings_by_username(nickname: str, db: Session = Depends(get_db)):

    user = (
        db.query(models.User)
        .filter(models.User.nickname == nickname)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    ratings = (
        db.query(models.Rating)
        .filter(models.Rating.user_id == user.id)
        .all()
    )

    if not ratings:
        raise HTTPException(
            status_code=404,
            detail="Ratings not found for the user"
        )

    return ratings

@app.get("/ratings/music/{music_id}", response_model=list[schemas.RatingResponse])
def get_ratings_by_music(music_id: int, db: Session = Depends(get_db)):

    ratings = (
        db.query(models.Rating)
        .filter(models.Rating.music_id == music_id)
        .all()
    )

    if not ratings:
        raise HTTPException(
            status_code=404,
            detail="Ratings not found for the music"
        )

    return ratings

# Update rating
@app.put("/ratings/{rating_id}", response_model=schemas.RatingResponse)
def update_rating(
    rating_id: int,
    data: schemas.RatingCreate,
    db: Session = Depends(get_db)
):

    rating = get_rating(rating_id=rating_id, db=db)

    if not rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found"
        )

    rating.user_id = data.user_id
    rating.music_id = data.music_id
    rating.rating = data.rating
    rating.description = data.description

    db.commit()
    db.refresh(rating)

    return rating

# Delete rating
@app.delete("/ratings/{rating_id}")
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db)
):

    rating = get_rating(rating_id=rating_id, db=db)

    if not rating:
        raise HTTPException(
            status_code=404,
            detail="Rating not found"
        )

    db.delete(rating)
    db.commit()

    return {
        "message": "Rating deleted successfully"
    }

@app.get("/spotify/music/id/{id}", response_model=dict)
def search_spotify(id: str):
    
    return sp.get_music_by_id(music_id=id)
    
@app.get("/spotify/music/artists/{id}", response_model=str)
def get_artists_spotify(id: str):
    
    return sp.get_artists_by_music(music=sp.get_music_by_id(id))