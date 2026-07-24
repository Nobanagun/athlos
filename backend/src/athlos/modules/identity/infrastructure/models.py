"""ORM mapping for the identity bounded context.

`User`/`Device` (domain/) stay framework-free: this module maps them via
private declarative subclasses, `_MappedUser`/`_MappedDevice`, so that
`identity/domain` never imports SQLAlchemy. Instances of those mapped
classes are what get added to a session, so
`SqlAlchemyUnitOfWork._tracked_aggregates()` (platform, unchanged) still
finds them via `isinstance(obj, AggregateRoot)` - no change to the
shared kernel was needed for this.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, String, TypeDecorator, UniqueConstraint, Uuid
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column

from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.user import AccountStatus, User
from athlos.modules.identity.domain.value_objects import (
    DeviceId,
    DeviceLinkId,
    Email,
    PasswordHash,
    UserId,
)
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


class PasswordHashType(TypeDecorator[PasswordHash]):
    """Persists a `PasswordHash` value object as its underlying `str`."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: PasswordHash | None, dialect: Dialect) -> str | None:
        return value.value if value is not None else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> PasswordHash | None:
        return PasswordHash(value) if value is not None else None


class DeviceLinkIdType(TypeDecorator[DeviceLinkId]):
    """Persists a `DeviceLinkId` value object as its underlying `uuid.UUID`."""

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value: DeviceLinkId | None, dialect: Dialect) -> uuid.UUID | None:
        return value.value if value is not None else None

    def process_result_value(
        self, value: uuid.UUID | None, dialect: Dialect
    ) -> DeviceLinkId | None:
        return DeviceLinkId(value) if value is not None else None


class DeviceIdType(TypeDecorator[DeviceId]):
    """Persists a `DeviceId` value object as its underlying `uuid.UUID`."""

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value: DeviceId | None, dialect: Dialect) -> uuid.UUID | None:
        return value.value if value is not None else None

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> DeviceId | None:
        return DeviceId(value) if value is not None else None


class UtcDateTimeType(TypeDecorator[datetime]):
    """Persists a timezone-aware UTC `datetime`, round-tripping correctly
    through SQLite - which silently discards `tzinfo` on plain
    `DateTime` columns (verified empirically: a value read back in the
    same process compared unequal to the one written, differing only by
    `tzinfo`). Stores as UTC-naive, reattaches `tzinfo=UTC` on read, so
    `Device.registered_at` is always timezone-aware regardless of
    whether it came fresh from `Device.register()` or was loaded back
    from the database (see docs/DECISIONS.md).
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


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
    password_hash: Mapped[PasswordHash] = mapped_column(PasswordHashType, nullable=False)
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
        mapped = cls(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            status=user.status,
        )
        for event in user.domain_events:
            mapped.record_event(event)
        return mapped


class _MappedDevice(Device, Base):
    """Private ORM mapping of `Device` - never import this outside
    `identity/infrastructure/`. `Device` comes first in the base list,
    same convention as `_MappedUser`.
    """

    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("device_id", "user_id", name="uq_devices_device_id_user_id"),
    )

    id: Mapped[DeviceLinkId] = mapped_column(DeviceLinkIdType, primary_key=True)
    device_id: Mapped[DeviceId] = mapped_column(DeviceIdType, nullable=False)
    user_id: Mapped[UserId] = mapped_column(UserIdType, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(UtcDateTimeType, nullable=False)

    @classmethod
    def from_domain(cls, device: Device) -> "_MappedDevice":
        """Wrap a plain `Device` (as returned by `Device.register()`,
        which the application layer calls on the base class) into its
        mapped, persistable form - carrying over any pending domain
        events. Same reasoning as `_MappedUser.from_domain()`.
        """
        mapped = cls(
            id=device.id,
            device_id=device.device_id,
            user_id=device.user_id,
            registered_at=device.registered_at,
        )
        for event in device.domain_events:
            mapped.record_event(event)
        return mapped
