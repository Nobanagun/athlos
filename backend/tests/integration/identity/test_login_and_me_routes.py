"""Integration tests for the identity HTTP interface (POST /login, GET
/users/me) - the JWT stateless authentication increment.

The `client`/`session`/`_jwt_secret` fixtures live in `conftest.py`,
shared with the other identity route test modules.
"""

import pytest
from fastapi.testclient import TestClient


def _register(
    client: TestClient, email: str = "alice@example.com", password: str = "s3cret!!"
) -> None:
    response = client.post("/users", json={"email": email, "password": password})
    assert response.status_code == 201


def test_login_with_correct_credentials_returns_a_bearer_token(client: TestClient) -> None:
    _register(client)

    response = client.post("/login", json={"email": "alice@example.com", "password": "s3cret!!"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    _register(client)

    response = client.post("/login", json={"email": "alice@example.com", "password": "wrong"})

    assert response.status_code == 401


def test_login_with_unknown_email_returns_401(client: TestClient) -> None:
    response = client.post("/login", json={"email": "nobody@example.com", "password": "whatever1"})

    assert response.status_code == 401


def test_get_me_with_valid_token_returns_the_authenticated_user(client: TestClient) -> None:
    _register(client)
    login_response = client.post(
        "/login", json={"email": "alice@example.com", "password": "s3cret!!"}
    )
    token = login_response.json()["access_token"]

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_get_me_without_a_token_returns_401(client: TestClient) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_me_with_an_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get("/users/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_get_me_with_a_token_signed_with_a_different_secret_returns_401(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _register(client)
    login_response = client.post(
        "/login", json={"email": "alice@example.com", "password": "s3cret!!"}
    )
    token = login_response.json()["access_token"]

    monkeypatch.setenv("JWT_SECRET", "a-different-secret-also-32-bytes-long")

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
