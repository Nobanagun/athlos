"""Fixtures for identity integration tests: a real SQLite-backed session
and an HTTP test client wired to it.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from athlos.api.dependencies import get_session
from athlos.api.main import app

# Importing registers `users` into Base.metadata (identity's ORM mapping
# has to be loaded before create_all() for the table to exist).
from athlos.modules.identity.infrastructure import models as _identity_models  # noqa: F401
from athlos.platform.infrastructure.persistence.database import Base


@pytest.fixture
def engine() -> Iterator[Engine]:
    # StaticPool: a plain in-memory SQLite engine hands out a *different*,
    # empty in-memory database per connection/thread by default. Routes
    # tests exercise the app through TestClient, which runs sync FastAPI
    # dependencies in a worker thread - without StaticPool (a single
    # shared connection reused everywhere), that thread would see a
    # database that never had create_all() run against it.
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
