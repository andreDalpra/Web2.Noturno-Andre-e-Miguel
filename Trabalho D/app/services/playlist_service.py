from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao import PlaylistDAO, UserDAO, UserPlaylistDAO
from app.models import Playlist, PlaylistTrack, UserPlaylist
from app.schemas import PlaylistCreate, PlaylistUpdate


class PlaylistService:
    def __init__(self, db: Session):
        self.db = db
        self.playlists = PlaylistDAO(db)
        self.memberships = UserPlaylistDAO(db)
        self.users = UserDAO(db)

    def _get(self, playlist_id: int) -> Playlist:
        playlist = self.playlists.get_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    def _require_member(self, playlist_id: int, user_id: int) -> Playlist:
        playlist = self._get(playlist_id)
        if not self.memberships.get(user_id, playlist_id):
            raise HTTPException(status_code=403, detail="You are not a playlist participant")
        return playlist

    def _require_owner(self, playlist_id: int, user_id: int) -> Playlist:
        playlist = self._get(playlist_id)
        members = self.memberships.get_for_playlist(playlist_id)
        if not members or members[0].user_id != user_id:
            raise HTTPException(status_code=403, detail="Only the playlist owner can change it")
        return playlist

    def _response_data(self, playlist: Playlist) -> dict:
        return {
            "id": playlist.id,
            "name": playlist.name,
            "collaborative": playlist.collaborative,
            "created_at": playlist.created_at,
            "participants": [membership.user for membership in playlist.memberships],
            "spotify_ids": [track.spotify_id for track in playlist.tracks],
        }

    def create(self, data: PlaylistCreate, user_id: int) -> Playlist:
        playlist = self.playlists.create(Playlist(name=data.name, collaborative=data.collaborative))
        self.memberships.add(UserPlaylist(user_id=user_id, playlist_id=playlist.id))
        return self._get(playlist.id)

    def list_for_user(self, user_id: int) -> list[Playlist]:
        return self.playlists.get_for_user(user_id)

    def get_for_user(self, playlist_id: int, user_id: int) -> Playlist:
        return self._require_member(playlist_id, user_id)

    def update(self, playlist_id: int, data: PlaylistUpdate, user_id: int) -> Playlist:
        playlist = self._require_owner(playlist_id, user_id)
        playlist.name, playlist.collaborative = data.name, data.collaborative
        return self.playlists.save(playlist)

    def delete(self, playlist_id: int, user_id: int) -> None:
        playlist = self._require_owner(playlist_id, user_id)
        self.playlists.delete(playlist)

    def participants(self, playlist_id: int, user_id: int):
        playlist = self._require_member(playlist_id, user_id)
        return [membership.user for membership in playlist.memberships]

    def add_participant(self, playlist_id: int, nickname: str, user_id: int) -> Playlist:
        playlist = self._require_owner(playlist_id, user_id)
        if not playlist.collaborative:
            raise HTTPException(status_code=409, detail="Only collaborative playlists accept participants")
        participant = self.users.get_by_nickname(nickname)
        if not participant:
            raise HTTPException(status_code=404, detail="User with this nickname not found")
        if self.memberships.get(participant.id, playlist_id):
            raise HTTPException(status_code=409, detail="User already participates in this playlist")
        self.memberships.add(UserPlaylist(user_id=participant.id, playlist_id=playlist_id))
        return self._get(playlist_id)

    def remove_participant(self, playlist_id: int, nickname: str, user_id: int) -> None:
        playlist = self._require_owner(playlist_id, user_id)
        participant = self.users.get_by_nickname(nickname)
        if not participant:
            raise HTTPException(status_code=404, detail="User with this nickname not found")
        if participant.id == user_id:
            raise HTTPException(status_code=409, detail="The owner cannot leave the playlist")
        membership = self.memberships.get(participant.id, playlist.id)
        if not membership:
            raise HTTPException(status_code=404, detail="User is not a playlist participant")
        self.memberships.remove(membership)

    def add_track(self, playlist_id: int, spotify_id: str, user_id: int) -> Playlist:
        playlist = self._require_member(playlist_id, user_id)
        if self.playlists.get_track(playlist.id, spotify_id):
            raise HTTPException(status_code=409, detail="Music already belongs to this playlist")
        self.playlists.add_track(PlaylistTrack(
            playlist_id=playlist.id, spotify_id=spotify_id, position=len(playlist.tracks)
        ))
        return self._get(playlist.id)