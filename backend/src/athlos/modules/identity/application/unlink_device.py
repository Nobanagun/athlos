"""Use case: unlink a device from the authenticated user."""

from dataclasses import dataclass

from athlos.modules.identity.application.ports import DeviceRepository
from athlos.modules.identity.domain.exceptions import DeviceNotFoundError
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId


@dataclass(frozen=True)
class UnlinkDeviceCommand:
    user_id: UserId
    device_id: DeviceId


class UnlinkDeviceHandler:
    """Unlinks a device, raising `DeviceNotFoundError` if it does not
    exist or does not belong to `command.user_id` (see
    docs/DECISIONS.md - deliberately the same error in both cases).
    """

    def __init__(self, uow: UnitOfWork, devices: DeviceRepository) -> None:
        self._uow = uow
        self._devices = devices

    def handle(self, command: UnlinkDeviceCommand) -> None:
        device = self._devices.get_by_user_and_device_id(command.user_id, command.device_id)
        if device is None:
            raise DeviceNotFoundError()

        device.unlink()
        self._devices.remove(device)
        self._uow.commit()
