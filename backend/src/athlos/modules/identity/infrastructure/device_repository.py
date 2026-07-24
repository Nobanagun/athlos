"""SQLAlchemy-backed implementation of the identity device repository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.modules.identity.application.ports import DeviceRepository
from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.modules.identity.infrastructure.models import _MappedDevice
from athlos.platform.domain.user_id import UserId


class SqlAlchemyDeviceRepository(DeviceRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, device: Device) -> None:
        self._session.add(_MappedDevice.from_domain(device))

    def remove(self, device: Device) -> None:
        """`device` must already be a `_MappedDevice` loaded in this
        session (returned by `get_by_user_and_device_id`) - `session.
        delete()` needs the mapped instance so `SqlAlchemyUnitOfWork.
        _tracked_aggregates()` picks it up via `session.deleted` and
        stages its pending `DeviceUnlinked` event before the row is
        actually removed on commit.
        """
        self._session.delete(device)

    def get_by_user_and_device_id(self, user_id: UserId, device_id: DeviceId) -> Device | None:
        stmt = select(_MappedDevice).where(
            _MappedDevice.user_id == user_id, _MappedDevice.device_id == device_id
        )
        return self._session.scalars(stmt).first()

    def get_by_user(self, user_id: UserId) -> list[Device]:
        stmt = select(_MappedDevice).where(_MappedDevice.user_id == user_id)
        return list(self._session.scalars(stmt).all())
