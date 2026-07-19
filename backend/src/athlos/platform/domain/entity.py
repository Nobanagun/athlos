"""Base building blocks for entities and aggregate roots."""

from athlos.platform.domain.events import DomainEvent


class Entity[TId]:
    """Base for objects defined by identity, not by their attributes."""

    def __init__(self, id: TId) -> None:
        self.id = id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and bool(self.id == other.id)

    def __hash__(self) -> int:
        return hash((type(self), self.id))


class AggregateRoot[TId](Entity[TId]):
    """Entity that is the transactional consistency boundary for its
    sub-entities, and the source of domain events.
    """

    def __init__(self, id: TId) -> None:
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        """Non-destructive read of pending events (always a copy)."""
        return tuple(self._domain_events)

    def clear_domain_events(self) -> None:
        """Discard pending events.

        Call only after they are safely persisted elsewhere (e.g. once a
        Unit of Work's commit has succeeded) - never before, or a failure
        could silently drop events that were never actually saved.
        """
        self._domain_events.clear()
