"""Tests for RegisterDeviceHandler."""

import uuid

from athlos.modules.identity.application.register_device import (
    DeviceLinkResult,
    RegisterDeviceCommand,
    RegisterDeviceHandler,
)
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.identity.application._fakes import FakeUnitOfWork, InMemoryDeviceRepository

_USER_ID = UserId.generate()
_DEVICE_ID = DeviceId(uuid.uuid4())


def _handler() -> tuple[RegisterDeviceHandler, InMemoryDeviceRepository, FakeUnitOfWork]:
    devices = InMemoryDeviceRepository()
    uow = FakeUnitOfWork()
    return RegisterDeviceHandler(uow, devices), devices, uow


def test_handle_links_a_new_device_and_returns_its_data() -> None:
    handler, devices, uow = _handler()

    result = handler.handle(RegisterDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID))

    assert isinstance(result, DeviceLinkResult)
    assert result.device_id == _DEVICE_ID
    assert len(devices.add_calls) == 1
    assert uow.commit_count == 1


def test_handle_is_idempotent_for_the_same_user_and_device() -> None:
    handler, devices, uow = _handler()
    command = RegisterDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID)

    first = handler.handle(command)
    second = handler.handle(command)

    assert first.device_id == second.device_id
    assert first.registered_at == second.registered_at
    assert len(devices.add_calls) == 1
    assert uow.commit_count == 1


def test_handle_allows_the_same_device_id_for_different_users() -> None:
    handler, devices, _uow = _handler()
    other_user_id = UserId.generate()

    handler.handle(RegisterDeviceCommand(user_id=_USER_ID, device_id=_DEVICE_ID))
    handler.handle(RegisterDeviceCommand(user_id=other_user_id, device_id=_DEVICE_ID))

    assert len(devices.add_calls) == 2
