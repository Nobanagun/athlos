"""Tests for the GymActivity aggregate."""

from datetime import UTC, datetime

from athlos.modules.training.domain.events import ActivityRecorded
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.value_objects import Duration, Sport
from athlos.platform.domain.user_id import UserId

_USER_ID = UserId.generate()
_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_register_creates_the_activity_with_the_given_data() -> None:
    activity = GymActivity.register(_USER_ID, Duration(2700), _STARTED_AT)

    assert activity.user_id == _USER_ID
    assert activity.duration == Duration(2700)
    assert activity.started_at == _STARTED_AT
    assert activity.sport is Sport.GYM
    assert not hasattr(activity, "distance")


def test_register_records_exactly_one_activity_recorded_event() -> None:
    activity = GymActivity.register(_USER_ID, Duration(2700), _STARTED_AT)

    events = activity.domain_events
    assert len(events) == 1
    assert isinstance(events[0], ActivityRecorded)
    assert events[0].sport == "gym"
