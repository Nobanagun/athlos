"""Integration tests for the training HTTP interface."""

import uuid

from fastapi.testclient import TestClient


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_running_activity_returns_201_with_the_activity(
    client: TestClient, auth_token: str
) -> None:
    response = client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 3600,
            "started_at": "2026-07-24T08:00:00Z",
        },
        headers=_auth_headers(auth_token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sport"] == "running"
    assert body["distance_meters"] == 10_000
    assert body["duration_seconds"] == 3600


def test_register_gym_activity_has_no_distance_field(client: TestClient, auth_token: str) -> None:
    response = client.post(
        "/activities/gym",
        json={"duration_seconds": 2700, "started_at": "2026-07-24T08:00:00Z"},
        headers=_auth_headers(auth_token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sport"] == "gym"
    assert "distance_meters" not in body


def test_register_activity_without_a_token_returns_401(client: TestClient) -> None:
    response = client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 3600,
            "started_at": "2026-07-24T08:00:00Z",
        },
    )

    assert response.status_code == 401


def test_register_activity_with_non_positive_duration_returns_422(
    client: TestClient, auth_token: str
) -> None:
    response = client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 0,
            "started_at": "2026-07-24T08:00:00Z",
        },
        headers=_auth_headers(auth_token),
    )

    assert response.status_code == 422


def test_list_activities_returns_only_the_authenticated_user_activities(
    client: TestClient, auth_token: str
) -> None:
    client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 3600,
            "started_at": "2026-07-24T08:00:00Z",
        },
        headers=_auth_headers(auth_token),
    )
    client.post(
        "/activities/gym",
        json={"duration_seconds": 2700, "started_at": "2026-07-25T08:00:00Z"},
        headers=_auth_headers(auth_token),
    )

    response = client.get("/activities", headers=_auth_headers(auth_token))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    # most recent first
    assert body[0]["sport"] == "gym"
    assert body[1]["sport"] == "running"
    assert set(body[0].keys()) == {"id", "sport", "started_at"}


def test_get_running_activity_detail_returns_the_full_shape(
    client: TestClient, auth_token: str
) -> None:
    register_response = client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 3600,
            "started_at": "2026-07-24T08:00:00Z",
        },
        headers=_auth_headers(auth_token),
    )
    activity_id = register_response.json()["id"]

    response = client.get(f"/activities/running/{activity_id}", headers=_auth_headers(auth_token))

    assert response.status_code == 200
    assert response.json()["distance_meters"] == 10_000


def test_get_running_activity_that_does_not_exist_returns_404(
    client: TestClient, auth_token: str
) -> None:
    response = client.get(f"/activities/running/{uuid.uuid4()}", headers=_auth_headers(auth_token))

    assert response.status_code == 404


def test_get_running_activity_belonging_to_another_user_returns_404(
    client: TestClient, auth_token: str
) -> None:
    register_response = client.post(
        "/activities/running",
        json={
            "distance_meters": 10_000,
            "duration_seconds": 3600,
            "started_at": "2026-07-24T08:00:00Z",
        },
        headers=_auth_headers(auth_token),
    )
    activity_id = register_response.json()["id"]

    client.post("/users", json={"email": "other@example.com", "password": "s3cret!!"})
    other_login = client.post("/login", json={"email": "other@example.com", "password": "s3cret!!"})
    other_token = other_login.json()["access_token"]

    response = client.get(f"/activities/running/{activity_id}", headers=_auth_headers(other_token))

    assert response.status_code == 404
