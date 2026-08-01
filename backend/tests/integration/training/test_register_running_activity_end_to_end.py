"""End-to-end test: RegisterRunningActivityHandler wired with the real
repository and the real Unit of Work - no test doubles anywhere in this
file. Verifies the ActivityRecorded outbox row exists after a real
commit, same pattern as identity's test_register_user_end_to_end.py /
test_register_device_end_to_end.py.

Representative of the three sports - Cycling/Gym share the identical
handler/repository/UnitOfWork wiring, not repeated per sport (same
scope-trimming already applied to the repository tests).
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from athlos.modules.training.application.register_running_activity import (
    RegisterRunningActivityCommand,
    RegisterRunningActivityHandler,
)
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.modules.training.infrastructure.running_repository import (
    SqlAlchemyRunningActivityRepository,
)
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_register_running_activity_persists_and_stages_outbox_event(session: Session) -> None:
    repo = SqlAlchemyRunningActivityRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    handler = RegisterRunningActivityHandler(uow, repo)
    user_id = UserId.generate()

    result = handler.handle(
        RegisterRunningActivityCommand(
            user_id=user_id, distance_meters=10_000, duration_seconds=3600, started_at=_STARTED_AT
        )
    )

    assert isinstance(result, ActivityId)

    persisted = repo.get_by_user_and_id(user_id, result)
    assert persisted is not None

    outbox_row = session.query(OutboxMessage).filter_by(event_type="ActivityRecorded").one()
    assert outbox_row.processed_at is None
    assert outbox_row.payload["activity_id"] == str(result.value)
    assert outbox_row.payload["user_id"] == str(user_id.value)
    assert outbox_row.payload["sport"] == "running"
