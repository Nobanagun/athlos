"""SQLAlchemy-backed Unit of Work."""

from typing import Any

from sqlalchemy.orm import Session

from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.entity import AggregateRoot
from athlos.platform.infrastructure.outbox.models import OutboxMessage


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Persists aggregates and stages their pending domain events as outbox
    rows, atomically, in a single database transaction.

    `commit()` follows a fixed order:
    1. read (copy, non-destructively) the tracked aggregates and their
       pending events, exactly once;
    2. the aggregate itself is already staged in the session (`session.add`
       is the caller's responsibility, before calling `commit()`);
    3. stage the corresponding `OutboxMessage` rows in the same session;
    4. `session.commit()` - a single call, so the aggregate and its outbox
       rows land in the same transaction;
    5. only once step 4 succeeds, clear the events from the very same list
       of aggregates obtained in step 1 (never re-querying the session,
       since its new/dirty/deleted state is no longer meaningful after a
       commit).

    If anything raises before step 4 completes, the session is rolled back
    and the events are never cleared (step 1 was a copy, not a pop), so
    nothing is lost.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def commit(self) -> None:
        tracked = self._tracked_aggregates()

        for aggregate in tracked:
            for event in aggregate.domain_events:
                self.session.add(OutboxMessage.from_event(event))

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        for aggregate in tracked:
            aggregate.clear_domain_events()

    def rollback(self) -> None:
        self.session.rollback()

    def _tracked_aggregates(self) -> list[AggregateRoot[Any]]:
        """Aggregates with potentially pending events in the current session.

        Uses `session.new | session.dirty | session.deleted`: sufficient
        for this phase, where every aggregate with pending events is also
        new, modified or deleted from SQLAlchemy's point of view. Does not
        detect an aggregate that raises an event without any mapped
        attribute changing - see docs/DECISIONS.md for when this needs
        revisiting (e.g. an explicit registration API on the Unit of Work).

        Encapsulated in this single method precisely so that a future
        change to that mechanism stays localized here.
        """
        candidates = self.session.new | self.session.dirty | self.session.deleted
        return [obj for obj in candidates if isinstance(obj, AggregateRoot)]
