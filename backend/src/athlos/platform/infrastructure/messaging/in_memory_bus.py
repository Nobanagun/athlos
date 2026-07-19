"""In-process implementation of the event bus."""

from collections import defaultdict

from athlos.platform.application.event_bus import EventBus, EventHandler
from athlos.platform.domain.events import DomainEvent


class InMemoryEventBus(EventBus):
    """Synchronous, in-process event bus.

    Suitable while nothing consumes events across processes. Replace with a
    real broker-backed adapter (e.g. Redis) once a cross-process consumer
    actually exists - see docs/DECISIONS.md.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
