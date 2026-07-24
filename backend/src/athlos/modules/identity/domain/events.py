"""Domain events for the identity bounded context."""

from dataclasses import dataclass

from athlos.platform.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserRegistered(DomainEvent):
    """A user was registered.

    Fields are plain `str`, not `UserId`/`Email` value objects:
    `OutboxMessage.from_event()` (platform/infrastructure/outbox) builds
    its JSON payload via `dataclasses.asdict()`, which assumes
    JSON-primitive fields - a raw `uuid.UUID` field would fail to
    serialize.
    """

    user_id: str
    email: str


@dataclass(frozen=True, kw_only=True)
class DeviceLinked(DomainEvent):
    """A device was linked to a user. Fields are plain `str`, not value
    objects - same reason as `UserRegistered`.
    """

    device_link_id: str
    device_id: str
    user_id: str


@dataclass(frozen=True, kw_only=True)
class DeviceUnlinked(DomainEvent):
    """A device was unlinked from a user."""

    device_link_id: str
    device_id: str
    user_id: str
