"""ORM mapping for the identity bounded context.

`User` (domain/user.py) stays framework-free: this module maps it via a
private declarative subclass, `_MappedUser`, so that `identity/domain`
never imports SQLAlchemy. `_MappedUser` instances are what gets added to
a session, so `SqlAlchemyUnitOfWork._tracked_aggregates()` (platform,
unchanged) still finds them via `isinstance(obj, AggregateRoot)` - no
change to the shared kernel was needed for this.
"""

import uuid

from sqlalchemy import Enum, String, TypeDecorator, Uuid
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column

from athlos.modules.identity.domain.user import AccountStatus, User
from athlos.modules.identity.domain.value_objects import Email, UserId
from athlos.platform.infrastructure.persistence.database import Base


class UserIdType(TypeDecorator[UserId]):
    """Persists a `UserId` value object as its underlying `uuid.UUID`."""

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value: UserId | None, dialect: Dialect) -> uuid.UUID | None:
        return value.value if value is not None else None

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> UserId | None:
        return UserId(value) if value is not None else None


class EmailType(TypeDecorator[Email]):
    """Persists an `Email` value object as its underlying `str`."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Email | None, dialect: Dialect) -> str | None:
        return value.value if value is not None else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> Email | None:
        return Email(value) if value is not None else None


class _MappedUser(User, Base):
    """Private ORM mapping of `User` - never import this outside
    `identity/infrastructure/`. `User` comes first in the base list so
    its identity-based `__eq__`/`__hash__` take priority over the
    declarative base (same convention as `DummyAggregate` in
    `backend/tests/unit/platform/_fixtures.py`, Fase 2).
    """

    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(UserIdType, primary_key=True)
    email: Mapped[Email] = mapped_column(EmailType, unique=True, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), nullable=False)

    @classmethod
    def from_domain(cls, user: User) -> "_MappedUser":
        """Wrap a plain `User` (as returned by `User.register()`, which
        the application layer calls on the base class) into its mapped,
        persistable form - carrying over any pending domain events.

        Needed because `User.register()` uses `cls(...)`, but the
        application layer only ever calls it on the base `User` class, so
        it never produces a `_MappedUser` on its own.
        """
        mapped = cls(id=user.id, email=user.email, status=user.status)
        for event in user.domain_events:
            mapped.record_event(event)
        return mapped
