from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth_controller import router as auth_router
from app.controllers.playlist_controller import router as playlist_router
from app.controllers.rating_controller import router as rating_router
from app.controllers.spotify_controller import router as spotify_router
from app.controllers.user_controller import router as user_router
from app.database import Base, engine
from app.models import Playlist, PlaylistTrack, Rating, User, UserPlaylist

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Music Reviews API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(rating_router)
app.include_router(playlist_router)
app.include_router(spotify_router)
