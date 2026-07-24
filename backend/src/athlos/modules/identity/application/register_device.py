"""Use case: link a device to the authenticated user."""

from dataclasses import dataclass
from datetime import datetime

from athlos.modules.identity.application.ports import DeviceRepository
from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.value_objects import DeviceId, UserId
from athlos.platform.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class RegisterDeviceCommand:
    user_id: UserId
    device_id: DeviceId


@dataclass(frozen=True)
class DeviceLinkResult:
    """Purpose-built result of registering a device - `device_id` and
    `registered_at` only, not the `Device` aggregate itself (would leak
    its internal event list past the application layer, same reasoning
    as `RegisterUserHandler` returning only `UserId`; see
    docs/DECISIONS.md). Lives here, not in `interfaces/`, since it is the
    handler's return contract, independent of any HTTP concern.
    """

    device_id: DeviceId
    registered_at: datetime


class RegisterDeviceHandler:
    """Links a device to a user, idempotently: registering the same
    `(device_id, user_id)` pair again returns the existing link without
    creating a new one or re-emitting `DeviceLinked` (see
    docs/DECISIONS.md).
    """

    def __init__(self, uow: UnitOfWork, devices: DeviceRepository) -> None:
        self._uow = uow
        self._devices = devices

    def handle(self, command: RegisterDeviceCommand) -> DeviceLinkResult:
        existing = self._devices.get_by_user_and_device_id(command.user_id, command.device_id)
        if existing is not None:
            return DeviceLinkResult(
                device_id=existing.device_id, registered_at=existing.registered_at
            )

        device = Device.register(command.device_id, command.user_id)
        self._devices.add(device)
        self._uow.commit()

        return DeviceLinkResult(device_id=device.device_id, registered_at=device.registered_at)
