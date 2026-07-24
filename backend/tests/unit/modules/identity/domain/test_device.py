"""Tests for the Device aggregate.

Entity/AggregateRoot identity equality is already covered generically in
backend/tests/unit/platform/ (Fase 2) - not repeated here.
"""

import uuid

from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.events import DeviceLinked, DeviceUnlinked
from athlos.modules.identity.domain.value_objects import DeviceId, UserId

_DEVICE_ID = DeviceId(uuid.uuid4())
_USER_ID = UserId.generate()


def test_register_links_the_device_to_the_user() -> None:
    device = Device.register(_DEVICE_ID, _USER_ID)

    assert device.device_id == _DEVICE_ID
    assert device.user_id == _USER_ID


def test_register_records_exactly_one_device_linked_event() -> None:
    device = Device.register(_DEVICE_ID, _USER_ID)

    events = device.domain_events
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, DeviceLinked)
    assert event.device_link_id == str(device.id.value)
    assert event.device_id == str(_DEVICE_ID.value)
    assert event.user_id == str(_USER_ID.value)


def test_two_registrations_of_the_same_device_id_produce_different_link_ids() -> None:
    """`DeviceLinkId`, not `device_id`, is this aggregate's identity - the
    same `device_id` linked twice (e.g. to two different users) yields
    two distinct `Device` instances (see docs/DECISIONS.md).
    """
    first = Device.register(_DEVICE_ID, _USER_ID)
    second = Device.register(_DEVICE_ID, UserId.generate())

    assert first.id != second.id


def test_unlink_records_exactly_one_device_unlinked_event() -> None:
    device = Device.register(_DEVICE_ID, _USER_ID)
    device.clear_domain_events()

    device.unlink()

    events = device.domain_events
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, DeviceUnlinked)
    assert event.device_link_id == str(device.id.value)
    assert event.device_id == str(_DEVICE_ID.value)
    assert event.user_id == str(_USER_ID.value)
