"""Tests for the CyclingActivity aggregate."""

from datetime import UTC, datetime

from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.events import ActivityRecorded
from athlos.modules.training.domain.value_objects import Distance, Duration, Sport
from athlos.platform.domain.user_id import UserId

_USER_ID = UserId.generate()
_STARTED_AT = datetime(2026, 7, 24, 8, 0, tzinfo=UTC)


def test_register_creates_the_activity_with_the_given_data() -> None:
    activity = CyclingActivity.register(_USER_ID, Distance(40_000), Duration(5400), _STARTED_AT)

    assert activity.user_id == _USER_ID
    assert activity.distance == Distance(40_000)
    assert activity.duration == Duration(5400)
    assert activity.started_at == _STARTED_AT
    assert activity.sport is Sport.CYCLING


def test_register_records_exactly_one_activity_recorded_event() -> None:
    activity = CyclingActivity.register(_USER_ID, Distance(40_000), Duration(5400), _STARTED_AT)

    events = activity.domain_events
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ActivityRecorded)
    assert event.sport == "cycling"
