"""Tests for ListUserActivitiesHandler."""

from datetime import UTC, datetime, timedelta

from athlos.modules.training.application.list_user_activities import ListUserActivitiesHandler
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import Distance, Duration, Sport
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.training.application._fakes import (
    InMemoryCyclingActivityRepository,
    InMemoryGymActivityRepository,
    InMemoryRunningActivityRepository,
)

_USER_ID = UserId.generate()
_NOW = datetime(2026, 7, 24, 12, 0, tzinfo=UTC)


def test_handle_merges_and_sorts_activities_across_sports_most_recent_first() -> None:
    running = InMemoryRunningActivityRepository()
    cycling = InMemoryCyclingActivityRepository()
    gym = InMemoryGymActivityRepository()

    oldest = RunningActivity.register(
        _USER_ID, Distance(5000), Duration(1800), _NOW - timedelta(days=2)
    )
    middle = GymActivity.register(_USER_ID, Duration(2700), _NOW - timedelta(days=1))
    newest = CyclingActivity.register(_USER_ID, Distance(40_000), Duration(5400), _NOW)
    running.add(oldest)
    gym.add(middle)
    cycling.add(newest)

    handler = ListUserActivitiesHandler(running, cycling, gym)

    result = handler.handle(_USER_ID)

    assert [a.id for a in result] == [newest.id, middle.id, oldest.id]
    assert [a.sport for a in result] == [Sport.CYCLING, Sport.GYM, Sport.RUNNING]


def test_handle_only_returns_the_given_user_activities() -> None:
    running = InMemoryRunningActivityRepository()
    mine = RunningActivity.register(_USER_ID, Distance(5000), Duration(1800), _NOW)
    running.add(mine)
    running.add(RunningActivity.register(UserId.generate(), Distance(5000), Duration(1800), _NOW))

    handler = ListUserActivitiesHandler(
        running, InMemoryCyclingActivityRepository(), InMemoryGymActivityRepository()
    )

    result = handler.handle(_USER_ID)

    assert [a.id for a in result] == [mine.id]


def test_handle_returns_an_empty_list_for_a_user_with_no_activities() -> None:
    handler = ListUserActivitiesHandler(
        InMemoryRunningActivityRepository(),
        InMemoryCyclingActivityRepository(),
        InMemoryGymActivityRepository(),
    )

    assert handler.handle(UserId.generate()) == []
