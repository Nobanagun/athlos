"""Fixtures for training integration tests: a real SQLite-backed session
and an HTTP test client wired to it. Imports identity's ORM mapping too
- registering/logging in a real user is a prerequisite for exercising
any protected training route.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from athlos.api.dependencies import get_session
from athlos.api.main import app

# Importing registers the identity and training tables into
# Base.metadata (ORM mapping has to be loaded before create_all() for
# them to exist).
from athlos.modules.identity.infrastructure import models as _identity_models  # noqa: F401
from athlos.modules.training.infrastructure import models as _training_models  # noqa: F401
from athlos.platform.infrastructure.persistence.database import Base


@pytest.fixture
def engine() -> Iterator[Engine]:
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(bind=engine)
    with factory() as sess:
        yield sess


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    def override_get_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-not-for-production-32-bytes")


@pytest.fixture
def auth_token(client: TestClient) -> str:
    """Registers and logs in a real user, returning a valid bearer
    token - the prerequisite for every protected training route.
    """
    email = "athlete@example.com"
    password = "s3cret!!"
    client.post("/users", json={"email": email, "password": password})
    response = client.post("/login", json={"email": email, "password": password})
    token: str = response.json()["access_token"]
    return token
