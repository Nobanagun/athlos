"""Base building block for domain events."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Something relevant that happened in the domain.

    Immutable: once raised, an event's data cannot change.
    """

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
