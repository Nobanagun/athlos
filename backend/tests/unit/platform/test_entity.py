"""Tests for Entity identity semantics."""

import uuid

from athlos.platform.domain.entity import AggregateRoot, Entity
from athlos.platform.domain.events import DomainEvent


class ConcreteEntity(Entity[uuid.UUID]):
    pass


class ConcreteAggregate(AggregateRoot[uuid.UUID]):
    pass


def test_entities_with_same_id_are_equal() -> None:
    shared_id = uuid.uuid4()
    assert ConcreteEntity(shared_id) == ConcreteEntity(shared_id)


def test_entities_with_different_id_are_not_equal() -> None:
    assert ConcreteEntity(uuid.uuid4()) != ConcreteEntity(uuid.uuid4())


def test_entity_hash_is_based_on_id() -> None:
    shared_id = uuid.uuid4()
    assert hash(ConcreteEntity(shared_id)) == hash(ConcreteEntity(shared_id))


def test_normal_construction_behavior_is_unchanged() -> None:
    """Baseline: an aggregate constructed the normal way (through
    __init__) records, reads and clears events exactly as before.
    """
    aggregate = ConcreteAggregate(uuid.uuid4())
    event = DomainEvent()

    aggregate.record_event(event)
    assert aggregate.domain_events == (event,)

    aggregate.clear_domain_events()
    assert len(aggregate.domain_events) == 0


def test_domain_events_on_object_created_via_new_does_not_crash() -> None:
    """An instance brought into existence without __init__ running (as
    an ORM does when loading a row) must behave as if it has no pending
    events, not raise AttributeError.
    """
    aggregate = ConcreteAggregate.__new__(ConcreteAggregate)

    assert aggregate.domain_events == ()


def test_record_event_initializes_list_when_missing() -> None:
    aggregate = ConcreteAggregate.__new__(ConcreteAggregate)
    event = DomainEvent()

    aggregate.record_event(event)

    assert aggregate.domain_events == (event,)


def test_clear_domain_events_is_a_no_op_when_list_missing() -> None:
    aggregate = ConcreteAggregate.__new__(ConcreteAggregate)

    aggregate.clear_domain_events()  # must not raise

    assert aggregate.domain_events == ()
