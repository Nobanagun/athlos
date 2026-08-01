"""Tests for the three RegisterXActivityHandler use cases."""

from datetime import UTC, datetime

from athlos.modules.training.application.register_cycling_activity import (
    RegisterCyclingActivityCommand,
    RegisterCyclingActivityHandler,
)
from athlos.modules.training.application.register_gym_activity import (
    RegisterGymActivityCommand,
    RegisterGymActivityHandler,
)
from athlos.modules.training.application.register_running_activity import (
    RegisterRunningActivityCommand,
    RegisterRunningActivityHandler,
)
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.training.application._fakes import (
    FakeUnitOfWork,
    InMemoryCyclingActivityRepository,
    InMemoryGymActivityRepository,
    InMemoryRunningActivityRepository,
)

_USER_ID = UserId.generate()
_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_register_running_activity_persists_and_commits() -> None:
    repo = InMemoryRunningActivityRepository()
    uow = FakeUnitOfWork()
    handler = RegisterRunningActivityHandler(uow, repo)

    result = handler.handle(
        RegisterRunningActivityCommand(
            user_id=_USER_ID, distance_meters=10_000, duration_seconds=3600, started_at=_STARTED_AT
        )
    )

    assert isinstance(result, ActivityId)
    assert len(repo.activities) == 1
    assert repo.activities[0].id == result
    assert uow.commit_count == 1


def test_register_cycling_activity_persists_and_commits() -> None:
    repo = InMemoryCyclingActivityRepository()
    uow = FakeUnitOfWork()
    handler = RegisterCyclingActivityHandler(uow, repo)

    result = handler.handle(
        RegisterCyclingActivityCommand(
            user_id=_USER_ID, distance_meters=40_000, duration_seconds=5400, started_at=_STARTED_AT
        )
    )

    assert isinstance(result, ActivityId)
    assert len(repo.activities) == 1
    assert uow.commit_count == 1


def test_register_gym_activity_persists_and_commits() -> None:
    repo = InMemoryGymActivityRepository()
    uow = FakeUnitOfWork()
    handler = RegisterGymActivityHandler(uow, repo)

    result = handler.handle(
        RegisterGymActivityCommand(user_id=_USER_ID, duration_seconds=2700, started_at=_STARTED_AT)
    )

    assert isinstance(result, ActivityId)
    assert len(repo.activities) == 1
    assert uow.commit_count == 1
