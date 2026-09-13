from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserPlaylist


class UserPlaylistDAO:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int, playlist_id: int) -> UserPlaylist | None:
        return self.db.scalar(select(UserPlaylist).where(
            UserPlaylist.user_id == user_id, UserPlaylist.playlist_id == playlist_id
        ))

    def get_for_playlist(self, playlist_id: int) -> list[UserPlaylist]:
        return list(self.db.scalars(select(UserPlaylist).where(UserPlaylist.playlist_id == playlist_id)).all())

    def add(self, membership: UserPlaylist) -> UserPlaylist:
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def remove(self, membership: UserPlaylist) -> None:
        self.db.delete(membership)
        self.db.commit()