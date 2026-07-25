"""Tests for the three GetXActivityHandler use cases."""

from datetime import UTC, datetime

import pytest

from athlos.modules.training.application.get_running_activity import GetRunningActivityHandler
from athlos.modules.training.domain.exceptions import ActivityNotFoundError
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.training.application._fakes import InMemoryRunningActivityRepository

_USER_ID = UserId.generate()
_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_handle_returns_the_activity_when_owned_by_the_user() -> None:
    repo = InMemoryRunningActivityRepository()
    activity = RunningActivity.register(_USER_ID, Distance(10_000), Duration(3600), _STARTED_AT)
    repo.add(activity)
    handler = GetRunningActivityHandler(repo)

    result = handler.handle(_USER_ID, activity.id)

    assert result is activity


def test_handle_raises_for_an_activity_that_does_not_exist() -> None:
    handler = GetRunningActivityHandler(InMemoryRunningActivityRepository())

    with pytest.raises(ActivityNotFoundError):
        handler.handle(_USER_ID, ActivityId.generate())


def test_handle_raises_for_an_activity_owned_by_another_user() -> None:
    repo = InMemoryRunningActivityRepository()
    activity = RunningActivity.register(_USER_ID, Distance(10_000), Duration(3600), _STARTED_AT)
    repo.add(activity)
    handler = GetRunningActivityHandler(repo)

    with pytest.raises(ActivityNotFoundError):
        handler.handle(UserId.generate(), activity.id)
