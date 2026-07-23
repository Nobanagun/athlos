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

    `_domain_events` is normally set by `__init__`, but instances can also
    come into existence without `__init__` ever running - notably, an ORM
    (SQLAlchemy) reconstitutes a loaded row via `__new__` plus direct
    attribute population, never calling `__init__`. `domain_events`,
    `record_event()` and `clear_domain_events()` therefore treat a
    missing `_domain_events` as "no events yet" instead of assuming it
    always exists, so a freshly loaded aggregate behaves like one with no
    pending events rather than raising `AttributeError`.
    """

    def __init__(self, id: TId) -> None:
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        if not hasattr(self, "_domain_events"):
            self._domain_events = []
        self._domain_events.append(event)

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        """Non-destructive read of pending events (always a copy)."""
        return tuple(getattr(self, "_domain_events", []))

    def clear_domain_events(self) -> None:
        """Discard pending events.

        Call only after they are safely persisted elsewhere (e.g. once a
        Unit of Work's commit has succeeded) - never before, or a failure
        could silently drop events that were never actually saved. A
        no-op if there is nothing to clear (e.g. an aggregate that was
        loaded, not constructed, and never recorded an event since).
        """
        if hasattr(self, "_domain_events"):
            self._domain_events.clear()
