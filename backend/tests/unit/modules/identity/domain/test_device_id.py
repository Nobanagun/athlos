"""Tests for the DeviceLinkId and DeviceId value objects."""

import uuid

from athlos.modules.identity.domain.value_objects import DeviceId, DeviceLinkId


def test_generated_device_link_ids_are_distinct() -> None:
    assert DeviceLinkId.generate() != DeviceLinkId.generate()


def test_device_link_ids_with_same_value_are_equal() -> None:
    shared = uuid.uuid4()
    assert DeviceLinkId(shared) == DeviceLinkId(shared)


def test_device_ids_with_same_value_are_equal() -> None:
    shared = uuid.uuid4()
    assert DeviceId(shared) == DeviceId(shared)


def test_device_ids_with_different_values_are_not_equal() -> None:
    assert DeviceId(uuid.uuid4()) != DeviceId(uuid.uuid4())
