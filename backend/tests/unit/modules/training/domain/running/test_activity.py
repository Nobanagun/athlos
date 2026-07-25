"""Tests for the RunningActivity aggregate."""

from datetime import UTC, datetime

from athlos.modules.training.domain.events import ActivityRecorded
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import Distance, Duration, Sport
from athlos.platform.domain.user_id import UserId

_USER_ID = UserId.generate()
_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_register_creates_the_activity_with_the_given_data() -> None:
    activity = RunningActivity.register(_USER_ID, Distance(10_000), Duration(3600), _STARTED_AT)

    assert activity.user_id == _USER_ID
    assert activity.distance == Distance(10_000)
    assert activity.duration == Duration(3600)
    assert activity.started_at == _STARTED_AT
    assert activity.sport is Sport.RUNNING


def test_register_records_exactly_one_activity_recorded_event() -> None:
    activity = RunningActivity.register(_USER_ID, Distance(10_000), Duration(3600), _STARTED_AT)

    events = activity.domain_events
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ActivityRecorded)
    assert event.activity_id == str(activity.id.value)
    assert event.user_id == str(_USER_ID.value)
    assert event.sport == "running"


def test_two_registrations_produce_different_activity_ids() -> None:
    first = RunningActivity.register(_USER_ID, Distance(5000), Duration(1800), _STARTED_AT)
    second = RunningActivity.register(_USER_ID, Distance(5000), Duration(1800), _STARTED_AT)

    assert first.id != second.id
