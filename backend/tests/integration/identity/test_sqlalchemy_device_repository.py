"""Integration tests for SqlAlchemyDeviceRepository against a real engine."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.modules.identity.infrastructure.device_repository import SqlAlchemyDeviceRepository
from athlos.platform.domain.user_id import UserId


def test_add_and_get_by_user_and_device_id_roundtrip_preserves_value_objects(
    session: Session,
) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    user_id = UserId.generate()
    device_id = DeviceId(uuid.uuid4())
    device = Device.register(device_id, user_id)

    repo.add(device)
    session.commit()

    fetched = repo.get_by_user_and_device_id(user_id, device_id)

    assert fetched is not None
    assert fetched.id == device.id
    assert fetched.device_id == device_id
    assert fetched.user_id == user_id
    # registered_at must round-trip as timezone-aware UTC, not just any
    # value - SQLite silently drops tzinfo on a plain DateTime column
    # (see UtcDateTimeType).
    assert fetched.registered_at == device.registered_at
    assert fetched.registered_at.tzinfo is not None


def test_get_by_user_and_device_id_returns_none_when_not_found(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)

    assert repo.get_by_user_and_device_id(UserId.generate(), DeviceId(uuid.uuid4())) is None


def test_get_by_user_returns_only_that_user_devices(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    user_id = UserId.generate()
    repo.add(Device.register(DeviceId(uuid.uuid4()), user_id))
    repo.add(Device.register(DeviceId(uuid.uuid4()), user_id))
    repo.add(Device.register(DeviceId(uuid.uuid4()), UserId.generate()))
    session.commit()

    found = repo.get_by_user(user_id)

    assert len(found) == 2
    assert all(device.user_id == user_id for device in found)


def test_same_device_id_can_be_linked_to_different_users(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    device_id = DeviceId(uuid.uuid4())
    first_user_id = UserId.generate()
    second_user_id = UserId.generate()

    repo.add(Device.register(device_id, first_user_id))
    repo.add(Device.register(device_id, second_user_id))
    session.commit()  # must not raise: unique only on (device_id, user_id)

    assert repo.get_by_user_and_device_id(first_user_id, device_id) is not None
    assert repo.get_by_user_and_device_id(second_user_id, device_id) is not None


def test_duplicate_device_id_and_user_id_violates_unique_constraint(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    user_id = UserId.generate()
    device_id = DeviceId(uuid.uuid4())
    repo.add(Device.register(device_id, user_id))
    session.commit()

    repo.add(Device.register(device_id, user_id))
    with pytest.raises(IntegrityError):
        session.commit()


def test_remove_deletes_the_device(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    user_id = UserId.generate()
    device_id = DeviceId(uuid.uuid4())
    device = Device.register(device_id, user_id)
    repo.add(device)
    session.commit()

    fetched = repo.get_by_user_and_device_id(user_id, device_id)
    assert fetched is not None
    repo.remove(fetched)
    session.commit()

    assert repo.get_by_user_and_device_id(user_id, device_id) is None
