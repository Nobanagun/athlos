"""Contract for the internal event bus."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from athlos.platform.domain.events import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus(ABC):
    """Publishes domain events to interested subscribers."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None: ...

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None: ...
