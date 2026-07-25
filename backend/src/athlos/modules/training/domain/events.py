"""Domain events for the training bounded context."""

from dataclasses import dataclass

from athlos.platform.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ActivityRecorded(DomainEvent):
    """An activity was recorded, regardless of sport.

    Deliberately generic and minimal - no sport-specific metrics in the
    payload (see docs/DECISIONS.md). A consumer needing more detail
    queries the activity by `activity_id` instead. `occurred_at` is
    inherited from `DomainEvent`, not redeclared here (same convention
    as `UserRegistered`/`DeviceLinked`). Fields are plain `str`, not
    value objects - `OutboxMessage.from_event()` serializes via
    `dataclasses.asdict()`, which needs JSON-primitive fields.
    """

    activity_id: str
    user_id: str
    sport: str
