"""Fixtures for identity integration tests: a real SQLite-backed session."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

# Importing registers `users` into Base.metadata (identity's ORM mapping
# has to be loaded before create_all() for the table to exist).
from athlos.modules.identity.infrastructure import models as _identity_models  # noqa: F401
from athlos.platform.infrastructure.persistence.database import Base


@pytest.fixture
def engine() -> Iterator[Engine]:
    eng = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(bind=engine)
    with factory() as sess:
        yield sess
