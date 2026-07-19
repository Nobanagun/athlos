"""Tests for dispatch_pending(): per-message delivery semantics."""

from sqlalchemy.orm import Session

from athlos.platform.infrastructure.messaging.in_memory_bus import InMemoryEventBus
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.outbox.service import dispatch_pending
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from tests.unit.platform._fixtures import DummyAggregate, DummyCreated

_EVENT_TYPES = {"DummyCreated": DummyCreated}


def _commit_new_aggregate(session: Session, name: str) -> DummyAggregate:
    aggregate = DummyAggregate.create(name=name)
    session.add(aggregate)
    SqlAlchemyUnitOfWork(session).commit()
    return aggregate


def test_dispatch_pending_marks_processed_and_delivers_event(session: Session) -> None:
    _commit_new_aggregate(session, "dana")

    bus = InMemoryEventBus()
    received: list[DummyCreated] = []
    bus.subscribe(DummyCreated, received.append)  # type: ignore[arg-type]

    dispatch_pending(session, bus, event_types=_EVENT_TYPES)

    assert len(received) == 1
    assert received[0].name == "dana"

    message = session.query(OutboxMessage).one()
    assert message.processed_at is not None


def test_dispatch_pending_does_not_mark_processed_when_bus_fails(session: Session) -> None:
    _commit_new_aggregate(session, "erin")

    bus = InMemoryEventBus()

    def _boom(_event: DummyCreated) -> None:
        raise RuntimeError("handler failure")

    bus.subscribe(DummyCreated, _boom)  # type: ignore[arg-type]

    dispatch_pending(session, bus, event_types=_EVENT_TYPES)

    message = session.query(OutboxMessage).one()
    assert message.processed_at is None


def test_dispatch_pending_continues_after_one_failure(session: Session) -> None:
    _commit_new_aggregate(session, "first")
    _commit_new_aggregate(session, "second")

    bus = InMemoryEventBus()
    received: list[str] = []
    call_count = 0

    def _flaky(event: DummyCreated) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("fails only the first time")
        received.append(event.name)

    bus.subscribe(DummyCreated, _flaky)  # type: ignore[arg-type]

    dispatch_pending(session, bus, event_types=_EVENT_TYPES)

    processed = [m.processed_at for m in session.query(OutboxMessage).all()]
    assert processed.count(None) == 1
    assert received == ["second"]
