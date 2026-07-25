"""Fixtures for training integration tests: a real SQLite-backed session."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Importing registers the training tables into Base.metadata (ORM
# mapping has to be loaded before create_all() for them to exist).
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
