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
