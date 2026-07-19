"""Tests for SqlAlchemyUnitOfWork: atomicity and event lifecycle."""

import pytest
from sqlalchemy.orm import Session

from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from tests.unit.platform._fixtures import DummyAggregate


def test_commit_persists_aggregate_and_writes_outbox_in_same_transaction(
    session: Session,
) -> None:
    aggregate = DummyAggregate.create(name="alice")
    session.add(aggregate)

    SqlAlchemyUnitOfWork(session).commit()

    persisted = session.get(DummyAggregate, aggregate.id)
    assert persisted is not None

    outbox_rows = session.query(OutboxMessage).all()
    assert len(outbox_rows) == 1
    assert outbox_rows[0].event_type == "DummyCreated"
    assert outbox_rows[0].processed_at is None


def test_commit_clears_events_only_after_success(session: Session) -> None:
    aggregate = DummyAggregate.create(name="bob")
    session.add(aggregate)
    assert len(aggregate.domain_events) == 1

    SqlAlchemyUnitOfWork(session).commit()

    assert len(aggregate.domain_events) == 0


def test_failed_commit_rolls_back_and_keeps_events_in_memory(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    aggregate = DummyAggregate.create(name="carol")
    session.add(aggregate)

    def _boom() -> None:
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(session, "commit", _boom)

    with pytest.raises(RuntimeError):
        SqlAlchemyUnitOfWork(session).commit()

    # Events were only ever copied, never popped, so nothing is lost.
    assert len(aggregate.domain_events) == 1

    # Rollback undid both the aggregate and its outbox row in the same tx.
    assert session.query(OutboxMessage).all() == []
