"""Tests for InMemoryEventBus."""

from dataclasses import dataclass

from athlos.platform.domain.events import DomainEvent
from athlos.platform.infrastructure.messaging.in_memory_bus import InMemoryEventBus


@dataclass(frozen=True, kw_only=True)
class SampleEvent(DomainEvent):
    value: int


@dataclass(frozen=True, kw_only=True)
class OtherEvent(DomainEvent):
    pass


def test_publish_calls_subscribed_handlers() -> None:
    bus = InMemoryEventBus()
    received: list[SampleEvent] = []
    bus.subscribe(SampleEvent, received.append)  # type: ignore[arg-type]

    bus.publish(SampleEvent(value=42))

    assert len(received) == 1
    assert received[0].value == 42


def test_publish_ignores_unrelated_event_types() -> None:
    bus = InMemoryEventBus()
    received: list[SampleEvent] = []
    bus.subscribe(SampleEvent, received.append)  # type: ignore[arg-type]

    bus.publish(OtherEvent())

    assert received == []
