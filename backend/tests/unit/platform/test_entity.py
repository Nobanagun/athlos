"""Tests for Entity identity semantics."""

import uuid

from athlos.platform.domain.entity import Entity


class ConcreteEntity(Entity[uuid.UUID]):
    pass


def test_entities_with_same_id_are_equal() -> None:
    shared_id = uuid.uuid4()
    assert ConcreteEntity(shared_id) == ConcreteEntity(shared_id)


def test_entities_with_different_id_are_not_equal() -> None:
    assert ConcreteEntity(uuid.uuid4()) != ConcreteEntity(uuid.uuid4())


def test_entity_hash_is_based_on_id() -> None:
    shared_id = uuid.uuid4()
    assert hash(ConcreteEntity(shared_id)) == hash(ConcreteEntity(shared_id))
