"""Shared fixtures for the shared kernel's own tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from athlos.platform.infrastructure.persistence.database import Base
from tests.unit.platform._fixtures import TestBase


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as sess:
        yield sess
    engine.dispose()
