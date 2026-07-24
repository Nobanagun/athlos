"""Shared FastAPI dependencies: Session and Unit of Work.

Agnostic of any business module - only shared-kernel concepts
(`Session`, `UnitOfWork`) live here. Module-specific dependencies (e.g.
`identity`'s repository/handler) belong in that module's own
`interfaces/dependencies.py`, built on top of these.
"""

from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from athlos.config.settings import get_database_url
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.infrastructure.persistence.database import create_engine_and_session_factory
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


@lru_cache
def _get_session_factory() -> sessionmaker[Session]:
    """Built lazily, on first real use - not at import time.

    Importing this module must never require `DATABASE_URL` to be set:
    tests replace `get_session` entirely via `app.dependency_overrides`
    before any request is made, and must be able to import the app
    without a database configured.
    """
    _, session_factory = create_engine_and_session_factory(get_database_url())
    return session_factory


def get_session() -> Iterator[Session]:
    with _get_session_factory()() as session:
        yield session


def get_unit_of_work(session: Session = Depends(get_session)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)
