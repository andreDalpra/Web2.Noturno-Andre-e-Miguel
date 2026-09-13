import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_artists_by_music(self, music: dict) -> str:
        return ", ".join(artist["name"] for artist in music["artists"])

    def get_music_by_id(self, music_id: str) -> dict:
        return self.sp.track(music_id)

    def get_info(self, name: str) -> pd.DataFrame:
        result = []
        try:
            search = self.sp.search(q=name, type="album,track,episode")
            for music in search["tracks"]["items"][:50]:
                result.append({
                    "Nome": music["name"],
                    "Album": music["album"]["name"],
                    "Artista": self.get_artists_by_music(music),
                })
        except Exception:
            pass
        return pd.DataFrame(result)

    def get_music(self, name: str, limit: int) -> dict:
        return self.sp.search(q=name, type="track", limit=limit)

    def get_musicID(self, music: dict) -> str:
        return music["tracks"]["items"][0]["id"]