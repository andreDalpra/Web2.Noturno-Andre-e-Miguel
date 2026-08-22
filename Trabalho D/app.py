import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

def get_music_artist(music:str):
    return ", ".join([artist['name'] for artist in music['artists']])

def get_info(name: str):
    resultado = []
    try:
        pesquisa = sp.search(q=name, type='album,track,episode')
        for i in range(50):
            musica = pesquisa['tracks']['items'][i]
            album = musica['album']
            resultado.append({'Nome': musica['name'],
                             'Album': album['name'],
                             'Artista': get_music_artist(musica)})
    except:
        return pd.DataFrame(resultado)
    


# Substitua com os dados do seu Dashboard do Spotify
CLIENT_ID = "518de8493526498b8b26b2ba5aaae4be"
CLIENT_SECRET = "96d289abdcda4a7f9a3385b0ea86817f"

# Autenticação automática
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Exemplo de consulta: Buscar informações sobre um artista
print(get_info("Urubu do Pix FM5"))
