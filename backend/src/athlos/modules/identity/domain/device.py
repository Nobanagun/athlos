"""The Device aggregate - a client device linked to a user."""

from datetime import UTC, datetime

from athlos.modules.identity.domain.events import DeviceLinked, DeviceUnlinked
from athlos.modules.identity.domain.value_objects import DeviceId, DeviceLinkId, UserId
from athlos.platform.domain.entity import AggregateRoot


class Device(AggregateRoot[DeviceLinkId]):
    """A device linked to a user. `register()` is the sole intended entry
    point for linking a new device - `__init__` stays public (Python has
    no real private constructors), but callers should not construct a
    `Device` directly.

    Identified by `DeviceLinkId` (server-generated), not by `device_id`
    (client-generated): the same `device_id` can be linked to several
    users, so `device_id` alone cannot serve as this aggregate's identity
    (see docs/DECISIONS.md).
    """

    def __init__(
        self, id: DeviceLinkId, device_id: DeviceId, user_id: UserId, registered_at: datetime
    ) -> None:
        super().__init__(id)
        self.device_id = device_id
        self.user_id = user_id
        self.registered_at = registered_at

    @classmethod
    def register(cls, device_id: DeviceId, user_id: UserId) -> "Device":
        device = cls(
            id=DeviceLinkId.generate(),
            device_id=device_id,
            user_id=user_id,
            registered_at=datetime.now(UTC),
        )
        device.record_event(
            DeviceLinked(
                device_link_id=str(device.id.value),
                device_id=str(device_id.value),
                user_id=str(user_id.value),
            )
        )
        return device

    def unlink(self) -> None:
        self.record_event(
            DeviceUnlinked(
                device_link_id=str(self.id.value),
                device_id=str(self.device_id.value),
                user_id=str(self.user_id.value),
            )
        )
