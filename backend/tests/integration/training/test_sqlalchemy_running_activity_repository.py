"""Integration tests for SqlAlchemyRunningActivityRepository against a
real engine. Representative of all three sport repositories - same
`_MappedX` + `TypeDecorator` pattern, not repeated per sport.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration
from athlos.modules.training.infrastructure.running_repository import (
    SqlAlchemyRunningActivityRepository,
)
from athlos.platform.domain.user_id import UserId

_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_add_and_get_by_user_and_id_roundtrip_preserves_value_objects(session: Session) -> None:
    repo = SqlAlchemyRunningActivityRepository(session)
    user_id = UserId.generate()
    activity = RunningActivity.register(user_id, Distance(10_000), Duration(3600), _STARTED_AT)

    repo.add(activity)
    session.commit()

    fetched = repo.get_by_user_and_id(user_id, activity.id)

    assert fetched is not None
    assert fetched.id == activity.id
    assert fetched.user_id == user_id
    assert fetched.distance == Distance(10_000)
    assert fetched.duration == Duration(3600)
    # timezone-aware roundtrip - see UtcDateTimeType (docs/DECISIONS.md).
    assert fetched.started_at == _STARTED_AT
    assert fetched.started_at.tzinfo is not None


def test_get_by_user_and_id_returns_none_for_another_users_activity(session: Session) -> None:
    repo = SqlAlchemyRunningActivityRepository(session)
    owner = UserId.generate()
    activity = RunningActivity.register(owner, Distance(5000), Duration(1800), _STARTED_AT)
    repo.add(activity)
    session.commit()

    assert repo.get_by_user_and_id(UserId.generate(), activity.id) is None


def test_get_by_user_and_id_returns_none_when_not_found(session: Session) -> None:
    repo = SqlAlchemyRunningActivityRepository(session)

    assert repo.get_by_user_and_id(UserId.generate(), ActivityId.generate()) is None


def test_get_by_user_returns_only_that_user_activities(session: Session) -> None:
    repo = SqlAlchemyRunningActivityRepository(session)
    user_id = UserId.generate()
    repo.add(RunningActivity.register(user_id, Distance(5000), Duration(1800), _STARTED_AT))
    repo.add(RunningActivity.register(user_id, Distance(8000), Duration(2400), _STARTED_AT))
    repo.add(
        RunningActivity.register(UserId.generate(), Distance(5000), Duration(1800), _STARTED_AT)
    )
    session.commit()

    found = repo.get_by_user(user_id)

    assert len(found) == 2
    assert all(a.user_id == user_id for a in found)
