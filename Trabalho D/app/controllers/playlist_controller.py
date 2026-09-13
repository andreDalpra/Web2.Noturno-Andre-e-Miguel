from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import ParticipantResponse, PlaylistCreate, PlaylistResponse, PlaylistUpdate, TrackCreate
from app.services import PlaylistService

router = APIRouter(prefix="/playlists", tags=["Playlists"])


def response(service: PlaylistService, playlist):
    return service._response_data(playlist)


@router.post("", response_model=PlaylistResponse, status_code=201)
def create_playlist(data: PlaylistCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return response(service, service.create(data, current_user.id))


@router.get("", response_model=list[PlaylistResponse])
def list_playlists(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return [response(service, playlist) for playlist in service.list_for_user(current_user.id)]


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist(playlist_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return response(service, service.get_for_user(playlist_id, current_user.id))


@router.put("/{playlist_id}", response_model=PlaylistResponse)
def update_playlist(playlist_id: int, data: PlaylistUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return response(service, service.update(playlist_id, data, current_user.id))


@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PlaylistService(db).delete(playlist_id, current_user.id)
    return {"message": "Playlist deleted successfully"}


@router.get("/{playlist_id}/users", response_model=list[ParticipantResponse])
def list_participants(playlist_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PlaylistService(db).participants(playlist_id, current_user.id)


@router.post("/{playlist_id}/users/{nickname}", response_model=PlaylistResponse)
def add_participant(playlist_id: int, nickname: str = Path(min_length=2), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return response(service, service.add_participant(playlist_id, nickname, current_user.id))


@router.delete("/{playlist_id}/users/{nickname}")
def remove_participant(playlist_id: int, nickname: str = Path(min_length=2), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PlaylistService(db).remove_participant(playlist_id, nickname, current_user.id)
    return {"message": "Participant removed successfully"}


@router.post("/{playlist_id}/tracks", response_model=PlaylistResponse)
def add_track(playlist_id: int, data: TrackCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PlaylistService(db)
    return response(service, service.add_track(playlist_id, data.spotify_id, current_user.id))