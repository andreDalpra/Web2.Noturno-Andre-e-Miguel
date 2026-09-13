import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    database = tmp_path_factory.mktemp("db") / "api.sqlite"
    os.environ["DATABASE_URL"] = f"sqlite:///{database}"
    from app import app
    return TestClient(app)


def register(client, nickname):
    response = client.post("/users", json={
        "nickname": nickname,
        "email": f"{nickname}@example.test",
        "password": "1234",
    })
    assert response.status_code == 201, response.text
    return response.json()


def auth(client, nickname):
    response = client.post("/auth/login", json={"identifier": nickname, "password": "1234"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    return {"Authorization": f"Bearer {body['access_token']}"}


def test_jwt_and_playlist_n_to_n(client):
    owner = register(client, "owner_test")
    guest = register(client, "guest_test")
    owner_headers = auth(client, "owner_test")
    guest_headers = auth(client, "guest_test")

    assert client.get("/users").status_code == 200
    assert client.post("/auth/login", json={"identifier": "owner_test", "password": "wrong"}).status_code == 401
    assert client.post("/playlists", json={"name": "Private"}).status_code == 401
    created = client.post("/playlists", headers=owner_headers, json={"name": "Shared", "collaborative": True})
    assert created.status_code == 201, created.text
    playlist_id = created.json()["id"]

    added = client.post(f"/playlists/{playlist_id}/users/guest_test", headers=owner_headers)
    assert added.status_code == 200, added.text
    assert {item["nickname"] for item in added.json()["participants"]} == {"owner_test", "guest_test"}
    assert len(client.get(f"/playlists/{playlist_id}/users", headers=owner_headers).json()) == 2
    assert client.post(f"/playlists/{playlist_id}/users/guest_test", headers=owner_headers).status_code == 409
    assert client.post(f"/playlists/{playlist_id}/tracks", headers=guest_headers, json={"spotify_id": "track-1"}).status_code == 200

    rating = client.post("/ratings", headers=owner_headers, json={
        "user_id": guest["id"], "music_id": "track-1", "rating": 4.5, "description": "Great"
    })
    assert rating.status_code == 201
    assert rating.json()["user_id"] == owner["id"]
    assert client.post("/ratings", json={"music_id": "track-1", "rating": 4.5, "description": "No token"}).status_code == 401

    updated = client.put(f"/playlists/{playlist_id}", headers=owner_headers, json={"name": "Shared updated", "collaborative": True})
    assert updated.status_code == 200 and updated.json()["name"] == "Shared updated"
    assert client.delete(f"/playlists/{playlist_id}/users/guest_test", headers=owner_headers).status_code == 200
    assert len(client.get(f"/playlists/{playlist_id}/users", headers=owner_headers).json()) == 1
    normal = client.post("/playlists", headers=owner_headers, json={"name": "Private", "collaborative": False}).json()
    assert client.post(f"/playlists/{normal['id']}/users/guest_test", headers=owner_headers).status_code == 409
    assert client.delete(f"/playlists/{normal['id']}", headers=owner_headers).status_code == 200
    assert client.delete(f"/playlists/{playlist_id}", headers=owner_headers).status_code == 200


def test_invalid_token_is_rejected(client):
    response = client.get("/playlists", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_permissions_persistence_and_openapi(client):
    owner = register(client, "owner_deep")
    guest = register(client, "guest_deep")
    outsider = register(client, "outsider_deep")
    owner_headers = auth(client, "owner_deep")
    guest_headers = auth(client, "guest_deep")
    outsider_headers = auth(client, "outsider_deep")

    created = client.post("/playlists", headers=owner_headers, json={"name": "Deep", "collaborative": True})
    playlist_id = created.json()["id"]
    assert client.post(f"/playlists/{playlist_id}/users/guest_deep", headers=owner_headers).status_code == 200
    assert client.get(f"/playlists/{playlist_id}", headers=guest_headers).status_code == 200
    assert client.get(f"/playlists/{playlist_id}", headers=outsider_headers).status_code == 403
    assert client.put(f"/playlists/{playlist_id}", headers=guest_headers, json={"name": "Hack", "collaborative": True}).status_code == 403
    assert client.post(f"/playlists/{playlist_id}/users/outsider_deep", headers=guest_headers).status_code == 403

    assert client.post(f"/playlists/{playlist_id}/tracks", headers=guest_headers, json={"spotify_id": "deep-track"}).status_code == 200
    assert client.post(f"/playlists/{playlist_id}/tracks", headers=guest_headers, json={"spotify_id": "deep-track"}).status_code == 409
    rating = client.post("/ratings", headers=owner_headers, json={"music_id": "deep-track", "rating": 4, "description": "Deep"})
    assert rating.status_code == 201
    assert client.put(f"/ratings/{rating.json()['id']}", headers=guest_headers, json={"rating": 2, "description": "No"}).status_code == 403
    assert client.put(f"/ratings/{rating.json()['id']}", headers=owner_headers, json={"rating": 4.25, "description": "Invalid"}).status_code == 422

    second = client.post("/playlists", headers=owner_headers, json={"name": "Second", "collaborative": False})
    assert second.status_code == 201
    assert len(client.get("/playlists", headers=owner_headers).json()) == 2
    assert client.get("/docs").status_code == 200
    openapi = client.get("/openapi.json").json()
    assert openapi["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    assert "/playlists/{playlist_id}/users/{nickname}" in openapi["paths"]