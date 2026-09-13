from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Playlist, PlaylistTrack


class PlaylistDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, playlist_id: int) -> Playlist | None:
        return self.db.get(Playlist, playlist_id)

    def get_for_user(self, user_id: int) -> list[Playlist]:
        return list(self.db.scalars(select(Playlist).join(Playlist.memberships).where(
            Playlist.memberships.any(user_id=user_id)
        )).unique().all())

    def create(self, playlist: Playlist) -> Playlist:
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def save(self, playlist: Playlist) -> Playlist:
        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def delete(self, playlist: Playlist) -> None:
        self.db.delete(playlist)
        self.db.commit()

    def get_track(self, playlist_id: int, spotify_id: str) -> PlaylistTrack | None:
        return self.db.scalar(select(PlaylistTrack).where(
            PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.spotify_id == spotify_id
        ))

    def add_track(self, track: PlaylistTrack) -> PlaylistTrack:
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track