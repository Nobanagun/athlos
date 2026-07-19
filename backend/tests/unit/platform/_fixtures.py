"""Test-only aggregate and persistence model for shared kernel tests.

Deliberately NOT part of `athlos.platform` or any bounded context: this is
scaffolding private to the shared kernel's own test suite, registered
against its own `TestBase` (never the shared kernel's `Base`) so it never
leaks into a real Alembic migration.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBaseNoMeta, Mapped, mapped_column

from athlos.platform.domain.entity import AggregateRoot
from athlos.platform.domain.events import DomainEvent


class TestBase(DeclarativeBaseNoMeta):
    """Declarative base private to these tests (never Base.metadata)."""


@dataclass(frozen=True, kw_only=True)
class DummyCreated(DomainEvent):
    name: str


class DummyAggregate(AggregateRoot[uuid.UUID], TestBase):
    """Test-only aggregate. `AggregateRoot` comes first in the MRO so its
    identity-based `__eq__`/`__hash__` take priority over the ORM base.
    """

    __tablename__ = "dummy_aggregates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __init__(self, id: uuid.UUID, name: str) -> None:
        AggregateRoot.__init__(self, id)
        self.name = name

    @classmethod
    def create(cls, name: str) -> "DummyAggregate":
        aggregate = cls(id=uuid.uuid4(), name=name)
        aggregate.record_event(DummyCreated(name=name))
        return aggregate
