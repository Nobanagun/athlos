"""Dispatch of pending outbox messages to the event bus."""

from collections.abc import Mapping
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.platform.application.event_bus import EventBus
from athlos.platform.domain.events import DomainEvent
from athlos.platform.infrastructure.outbox.models import OutboxMessage


def dispatch_pending(
    session: Session,
    bus: EventBus,
    event_types: Mapping[str, type[DomainEvent]],
) -> None:
    """Publish every unprocessed outbox message, one at a time.

    `event_types` maps a stored `event_type` name back to its concrete
    `DomainEvent` subclass; the shared kernel has no knowledge of which
    event types exist (that belongs to whichever module registers them),
    so the caller supplies the mapping.

    A message is marked `processed_at` only if `bus.publish()` succeeds for
    it. If publishing raises, that message is left unprocessed (retried on
    a future call) and the rest of the batch is still attempted - one
    failing message never blocks the others.
    """
    pending = session.scalars(
        select(OutboxMessage).where(OutboxMessage.processed_at.is_(None))
    ).all()

    for message in pending:
        event_cls = event_types[message.event_type]
        event = event_cls(
            event_id=message.id,
            occurred_at=message.occurred_at,
            **message.payload,
        )
        try:
            bus.publish(event)
        except Exception:  # noqa: BLE001 - isolate one failing message from the rest of the batch
            continue
        message.processed_at = datetime.now(UTC)
        session.commit()
