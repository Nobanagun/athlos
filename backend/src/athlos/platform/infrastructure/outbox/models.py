"""Outbox table: reliable, at-least-once delivery of domain events."""

import dataclasses
import uuid
from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from athlos.platform.domain.events import DomainEvent
from athlos.platform.infrastructure.persistence.database import Base

_EXCLUDED_PAYLOAD_FIELDS = {"event_id", "occurred_at"}


class OutboxMessage(Base):
    """A domain event staged for reliable delivery via the Outbox pattern."""

    __tablename__ = "outbox_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    payload: Mapped[dict[str, object]] = mapped_column(JSON)
    occurred_at: Mapped[datetime]
    processed_at: Mapped[datetime | None] = mapped_column(default=None)

    @classmethod
    def from_event(cls, event: DomainEvent) -> "OutboxMessage":
        """Build an outbox row from a domain event.

        Only the event's own fields (beyond `event_id`/`occurred_at`, which
        get dedicated columns) are stored as JSON payload. Assumes those
        extra fields are JSON-serializable primitives - true for this
        phase's test event; richer payloads may need explicit (de)serialization
        support when a real module needs it.
        """
        payload = {
            key: value
            for key, value in dataclasses.asdict(event).items()
            if key not in _EXCLUDED_PAYLOAD_FIELDS
        }
        return cls(
            id=event.event_id,
            event_type=type(event).__name__,
            payload=payload,
            occurred_at=event.occurred_at,
        )
