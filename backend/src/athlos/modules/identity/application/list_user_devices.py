"""Use case: list the authenticated user's linked devices."""

from athlos.modules.identity.application.ports import DeviceRepository
from athlos.modules.identity.domain.device import Device
from athlos.platform.domain.user_id import UserId


class ListUserDevicesHandler:
    """Read-only - no `UnitOfWork`, same criterion as `LoginUserHandler`."""

    def __init__(self, devices: DeviceRepository) -> None:
        self._devices = devices

    def handle(self, user_id: UserId) -> list[Device]:
        return self._devices.get_by_user(user_id)
