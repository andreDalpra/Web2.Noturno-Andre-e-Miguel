# Nota Musical

O projeto está dividido entre uma API Python/FastAPI e uma interface React. A API
usa MVC com Service Layer e DAO: `controllers/` recebe HTTP, `services/` aplica as
regras, `dao/` acessa o banco e `models/` representa as tabelas.

## Executar

Em um terminal, na raiz do projeto:

```powershell
uvicorn app.main:app --reload
```

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Caso a API use outra porta, crie
`frontend/.env.local` com `VITE_API_URL=http://127.0.0.1:SUA_PORTA`.

## Estrutura

- `app/application.py`: composição da aplicação FastAPI.
- `app/models/`: `User`, `Rating`, `Playlist`, `UserPlaylist` e `PlaylistTrack`.
- `app/dao/`: acesso exclusivo ao SQLAlchemy.
- `app/services/`: regras de negócio e permissões.
- `app/controllers/`: routers HTTP separados por domínio.
- `app/controllers/spotify_controller.py`: endpoints da integração Spotify.
- `app/auth/`: JWT Bearer e `get_current_user`.
- `frontend/`: React/Vite com login, reviews, playlists e busca Spotify.

## Banco e migração

O projeto não usa migrations. Ao iniciar, `Base.metadata.create_all` cria apenas as
tabelas ausentes (`playlists`, `user_playlist` e `playlist_tracks`) e preserva as
tabelas e dados existentes. Para uma base já existente, rode `uvicorn app.main:app` uma
vez com o MySQL disponível.

## Playlists e autenticação

O login em `POST /auth/login` retorna `access_token` e `user`. Operações protegidas
usam `Authorization: Bearer TOKEN`. O dono cria a playlist; playlists colaborativas
aceitam `POST /playlists/{id}/users/{nickname}`. A associação `user_playlist` tem
chave composta e impede duplicações. As músicas são mantidas somente como IDs do
Spotify em `playlist_tracks`, sem duplicar o catálogo externo.

## Testes

Com as dependências instaladas, execute `pytest -q`. Os testes usam SQLite temporário
e cobrem JWT válido/inválido, criação de playlist, relação N:N por nickname,
duplicidade, participante adicionando música e rating protegido.
