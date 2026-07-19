"""Tests for the DomainEvent base."""

import dataclasses

import pytest

from athlos.platform.domain.events import DomainEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class SomethingHappened(DomainEvent):
    detail: str


def test_domain_event_has_id_and_timestamp() -> None:
    event = SomethingHappened(detail="x")
    assert event.event_id is not None
    assert event.occurred_at is not None


def test_domain_event_is_immutable() -> None:
    event = SomethingHappened(detail="x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.detail = "y"  # type: ignore[misc]


def test_two_events_have_different_ids() -> None:
    assert SomethingHappened(detail="x").event_id != SomethingHappened(detail="x").event_id
