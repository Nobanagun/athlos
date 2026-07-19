"""Declarative base and engine/session factory for the shared kernel."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBaseNoMeta, Session, sessionmaker


class Base(DeclarativeBaseNoMeta):
    """Declarative base shared by every module's ORM models.

    Uses `DeclarativeBaseNoMeta` (not `DeclarativeBase`) so that aggregates
    can inherit from both this base and `AggregateRoot` (a plain Python
    class) without a metaclass conflict.
    """


def create_engine_and_session_factory(database_url: str) -> tuple[Engine, sessionmaker[Session]]:
    """Build a SQLAlchemy engine and a bound session factory for `database_url`."""
    engine = create_engine(database_url)
    session_factory = sessionmaker(bind=engine)
    return engine, session_factory
