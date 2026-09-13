from datetime import datetime

from sqlalchemy import Boolean, DateTime, Double, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    ratings: Mapped[list["Rating"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    playlist_memberships: Mapped[list["UserPlaylist"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    playlists: Mapped[list["Playlist"]] = relationship(
        secondary="user_playlist", back_populates="users", viewonly=True
    )


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    music_id: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[float] = mapped_column(Double, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user: Mapped[User] = relationship(back_populates="ratings")


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    collaborative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    users: Mapped[list[User]] = relationship(
        secondary="user_playlist", back_populates="playlists", viewonly=True
    )
    memberships: Mapped[list["UserPlaylist"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )
    tracks: Mapped[list["PlaylistTrack"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistTrack.position"
    )


class UserPlaylist(Base):
    __tablename__ = "user_playlist"
    __table_args__ = (UniqueConstraint("user_id", "playlist_id", name="uq_user_playlist"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True)
    user: Mapped[User] = relationship(back_populates="playlist_memberships")
    playlist: Mapped[Playlist] = relationship(back_populates="memberships")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    __table_args__ = (UniqueConstraint("playlist_id", "spotify_id", name="uq_playlist_track"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    spotify_id: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    playlist: Mapped[Playlist] = relationship(back_populates="tracks")