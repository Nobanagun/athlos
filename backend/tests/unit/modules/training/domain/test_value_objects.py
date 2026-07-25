"""Tests for training's shared value objects."""

import uuid

import pytest

from athlos.modules.training.domain.exceptions import InvalidDistanceError, InvalidDurationError
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration, Sport


def test_generated_activity_ids_are_distinct() -> None:
    assert ActivityId.generate() != ActivityId.generate()


def test_activity_ids_with_same_value_are_equal() -> None:
    shared = uuid.uuid4()
    assert ActivityId(shared) == ActivityId(shared)


def test_duration_accepts_a_positive_value() -> None:
    assert Duration(1800).seconds == 1800


@pytest.mark.parametrize("seconds", [0, -1, -3600])
def test_duration_rejects_non_positive_values(seconds: int) -> None:
    with pytest.raises(InvalidDurationError):
        Duration(seconds)


def test_distance_accepts_a_positive_value() -> None:
    assert Distance(5000.0).meters == 5000.0


@pytest.mark.parametrize("meters", [0, -1.0, -42.5])
def test_distance_rejects_non_positive_values(meters: float) -> None:
    with pytest.raises(InvalidDistanceError):
        Distance(meters)


def test_sport_values_match_the_three_supported_sports() -> None:
    assert {s.value for s in Sport} == {"running", "cycling", "gym"}
