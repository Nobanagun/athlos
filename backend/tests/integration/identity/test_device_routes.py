"""Integration tests for the identity HTTP interface (POST /devices, GET
/devices, DELETE /devices/{device_id}) - the linked devices increment.

The `client`/`session`/`_jwt_secret` fixtures live in `conftest.py`,
shared with the other identity route test modules.
"""

import uuid

from fastapi.testclient import TestClient


def _register_and_login(
    client: TestClient, email: str = "alice@example.com", password: str = "s3cret!!"
) -> str:
    response = client.post("/users", json={"email": email, "password": password})
    assert response.status_code == 201
    login_response = client.post("/login", json={"email": email, "password": password})
    token: str = login_response.json()["access_token"]
    return token


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_device_returns_200_with_the_device(client: TestClient) -> None:
    token = _register_and_login(client)
    device_id = str(uuid.uuid4())

    response = client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["device_id"] == device_id
    assert "registered_at" in body


def test_register_device_without_a_token_returns_401(client: TestClient) -> None:
    response = client.post("/devices", json={"device_id": str(uuid.uuid4())})

    assert response.status_code == 401


def test_register_device_twice_is_idempotent(client: TestClient) -> None:
    token = _register_and_login(client)
    device_id = str(uuid.uuid4())

    first = client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(token))
    second = client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(token))

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_list_devices_returns_only_the_authenticated_user_devices(client: TestClient) -> None:
    token = _register_and_login(client, email="alice@example.com")
    other_token = _register_and_login(client, email="bob@example.com")
    device_id = str(uuid.uuid4())
    client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(token))
    client.post(
        "/devices", json={"device_id": str(uuid.uuid4())}, headers=_auth_headers(other_token)
    )

    response = client.get("/devices", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["device_id"] == device_id


def test_list_devices_without_a_token_returns_401(client: TestClient) -> None:
    response = client.get("/devices")

    assert response.status_code == 401


def test_unlink_device_removes_it(client: TestClient) -> None:
    token = _register_and_login(client)
    device_id = str(uuid.uuid4())
    client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(token))

    response = client.delete(f"/devices/{device_id}", headers=_auth_headers(token))

    assert response.status_code == 204
    assert client.get("/devices", headers=_auth_headers(token)).json() == []


def test_unlink_unknown_device_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)

    response = client.delete(f"/devices/{uuid.uuid4()}", headers=_auth_headers(token))

    assert response.status_code == 404


def test_unlink_a_device_belonging_to_another_user_returns_404(client: TestClient) -> None:
    token = _register_and_login(client, email="alice@example.com")
    other_token = _register_and_login(client, email="bob@example.com")
    device_id = str(uuid.uuid4())
    client.post("/devices", json={"device_id": device_id}, headers=_auth_headers(other_token))

    response = client.delete(f"/devices/{device_id}", headers=_auth_headers(token))

    assert response.status_code == 404
    # still linked to its real owner
    assert len(client.get("/devices", headers=_auth_headers(other_token)).json()) == 1
