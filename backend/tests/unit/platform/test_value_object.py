"""Tests for ValueObject equality and immutability."""

import dataclasses
from dataclasses import dataclass

import pytest

from athlos.platform.domain.value_object import ValueObject


@dataclass(frozen=True)
class Money(ValueObject):
    amount: int
    currency: str


def test_value_objects_with_same_values_are_equal() -> None:
    assert Money(amount=10, currency="EUR") == Money(amount=10, currency="EUR")


def test_value_objects_with_different_values_are_not_equal() -> None:
    assert Money(amount=10, currency="EUR") != Money(amount=20, currency="EUR")


def test_value_object_is_immutable() -> None:
    money = Money(amount=10, currency="EUR")
    with pytest.raises(dataclasses.FrozenInstanceError):
        money.amount = 20  # type: ignore[misc]
