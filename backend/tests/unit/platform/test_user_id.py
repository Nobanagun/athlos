"""Tests for the UserId value object."""

import uuid

from athlos.platform.domain.user_id import UserId


def test_generated_ids_are_distinct() -> None:
    assert UserId.generate() != UserId.generate()


def test_ids_with_same_value_are_equal() -> None:
    shared = uuid.uuid4()
    assert UserId(shared) == UserId(shared)
