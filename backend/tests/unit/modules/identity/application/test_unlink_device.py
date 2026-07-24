"""Tests for UnlinkDeviceHandler."""

import uuid

import pytest

from athlos.modules.identity.application.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceHandler,
)
from athlos.modules.identity.application.unlink_device import (
    UnlinkDeviceCommand,
    UnlinkDeviceHandler,
)
from athlos.modules.identity.domain.exceptions import DeviceNotFoundError
from athlos.modules.identity.domain.value_objects import DeviceId, UserId
from tests.unit.modules.identity.application._fakes import FakeUnitOfWork, InMemoryDeviceRepository

_USER_ID = UserId.generate()
_DEVICE_ID = DeviceId(uuid.uuid4())


def test_handle_removes_a_linked_device() -> None:
    devices = InMemoryDeviceRepository()
    RegisterDeviceHandler(FakeUnitOfWork(), devices).handle(
        RegisterDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID)
    )
    uow = FakeUnitOfWork()
    handler = UnlinkDeviceHandler(uow, devices)

    handler.handle(UnlinkDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID))

    assert devices.get_by_user_and_device_id(_USER_ID, _DEVICE_ID) is None
    assert uow.commit_count == 1


def test_handle_raises_for_a_device_that_does_not_exist() -> None:
    handler = UnlinkDeviceHandler(FakeUnitOfWork(), InMemoryDeviceRepository())

    with pytest.raises(DeviceNotFoundError):
        handler.handle(UnlinkDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID))


def test_handle_raises_for_a_device_linked_to_a_different_user() -> None:
    devices = InMemoryDeviceRepository()
    RegisterDeviceHandler(FakeUnitOfWork(), devices).handle(
        RegisterDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID)
    )
    handler = UnlinkDeviceHandler(FakeUnitOfWork(), devices)
    someone_else = UserId.generate()

    with pytest.raises(DeviceNotFoundError):
        handler.handle(UnlinkDeviceCommand(user_id=someone_else, device_id=_DEVICE_ID))
