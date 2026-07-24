"""Tests for ListUserDevicesHandler."""

import uuid

from athlos.modules.identity.application.list_user_devices import ListUserDevicesHandler
from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.identity.application._fakes import InMemoryDeviceRepository


def test_handle_returns_only_the_given_user_devices() -> None:
    devices = InMemoryDeviceRepository()
    user_id = UserId.generate()
    other_user_id = UserId.generate()
    mine = Device.register(DeviceId(uuid.uuid4()), user_id)
    devices.add(mine)
    devices.add(Device.register(DeviceId(uuid.uuid4()), other_user_id))
    handler = ListUserDevicesHandler(devices)

    result = handler.handle(user_id)

    assert result == [mine]


def test_handle_returns_an_empty_list_for_a_user_with_no_devices() -> None:
    handler = ListUserDevicesHandler(InMemoryDeviceRepository())

    assert handler.handle(UserId.generate()) == []
