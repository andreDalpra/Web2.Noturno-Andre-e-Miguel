import os

from fastapi import APIRouter, Query

from app.spotify import SpotifyAPI

router = APIRouter(prefix="/spotify/music", tags=["Spotify"])
spotify = SpotifyAPI(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))


@router.get("/search", response_model=dict)
def search_music(query: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=20)):
    return spotify.get_music(query, limit)


@router.get("/id/{music_id}", response_model=dict)
def get_music(music_id: str):
    return spotify.get_music_by_id(music_id)


@router.get("/artists/{music_id}", response_model=str)
def get_artists(music_id: str):
    return spotify.get_artists_by_music(spotify.get_music_by_id(music_id))
