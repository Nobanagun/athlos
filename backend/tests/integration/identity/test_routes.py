"""Integration tests for the identity HTTP interface (POST /users).

The `client`/`session` fixtures live in `conftest.py`, shared with the
other identity route test modules.
"""

import uuid
from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from athlos.api.dependencies import get_session
from athlos.api.main import app
from athlos.modules.identity.domain.value_objects import Email
from athlos.modules.identity.infrastructure.repository import SqlAlchemyUserRepository
from athlos.modules.identity.interfaces.dependencies import get_user_repository
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.outbox.models import OutboxMessage


def test_register_user_returns_201_with_persisted_user_and_outbox_event(
    client: TestClient, session: Session
) -> None:
    response = client.post("/users", json={"email": "alice@example.com", "password": "s3cret!!"})

    assert response.status_code == 201
    body = response.json()
    user_id = UserId(uuid.UUID(body["id"]))

    repo = SqlAlchemyUserRepository(session)
    persisted = repo.get_by_id(user_id)
    assert persisted is not None
    assert persisted.email == Email("alice@example.com")

    outbox_row = session.query(OutboxMessage).filter_by(event_type="UserRegistered").one()
    assert outbox_row.processed_at is None


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    client.post("/users", json={"email": "bob@example.com", "password": "s3cret!!"})

    response = client.post("/users", json={"email": "bob@example.com", "password": "s3cret!!"})

    assert response.status_code == 409


def test_register_invalid_email_format_returns_422(client: TestClient) -> None:
    response = client.post("/users", json={"email": "not-an-email", "password": "s3cret!!"})

    assert response.status_code == 422


def test_register_missing_email_field_returns_422(client: TestClient) -> None:
    response = client.post("/users", json={"password": "s3cret!!"})

    assert response.status_code == 422


def test_register_weak_password_returns_422(client: TestClient) -> None:
    response = client.post("/users", json={"email": "weak@example.com", "password": "short"})

    assert response.status_code == 422


def test_register_missing_password_field_returns_422(client: TestClient) -> None:
    response = client.post("/users", json={"email": "alice@example.com"})

    assert response.status_code == 422


class _AlwaysMissRepository(SqlAlchemyUserRepository):
    """Test double that always reports "no existing user".

    Simulates the outcome of a race condition where two requests both
    pass the application-level uniqueness check before either commits -
    without needing real concurrent threads to reproduce it
    deterministically. `add()` is untouched, so the real UNIQUE
    constraint still fires inside commit().
    """

    def get_by_email(self, email: Email) -> None:
        return None


def test_race_condition_integrity_error_is_not_translated_and_surfaces_as_500(
    session: Session,
) -> None:
    """Documented, deliberate limitation for this increment (see
    docs/DECISIONS.md): a duplicate that slips past the
    application-level check and hits the real UNIQUE constraint inside
    commit() raises `IntegrityError`, which is not translated - it
    propagates and FastAPI's default handling turns it into a 500.
    """

    def override_get_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app, raise_server_exceptions=False)

    first = client.post("/users", json={"email": "race@example.com", "password": "s3cret!!"})
    assert first.status_code == 201

    app.dependency_overrides[get_user_repository] = lambda: _AlwaysMissRepository(session)
    try:
        second = client.post("/users", json={"email": "race@example.com", "password": "s3cret!!"})
    finally:
        app.dependency_overrides.clear()

    assert second.status_code == 500
