"""End-to-end test: RegisterDeviceHandler wired with the real repository
and the real Unit of Work - no test doubles anywhere in this file.
"""

import uuid

from sqlalchemy.orm import Session

from athlos.modules.identity.application.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceHandler,
)
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.modules.identity.infrastructure.device_repository import SqlAlchemyDeviceRepository
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_register_device_persists_and_stages_outbox_event(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    handler = RegisterDeviceHandler(uow, repo)
    user_id = UserId.generate()
    device_id = DeviceId(uuid.uuid4())

    result = handler.handle(RegisterDeviceCommand(user_id=user_id, device_id=device_id))

    assert result.device_id == device_id

    persisted = repo.get_by_user_and_device_id(user_id, device_id)
    assert persisted is not None

    outbox_row = session.query(OutboxMessage).filter_by(event_type="DeviceLinked").one()
    assert outbox_row.processed_at is None
    assert outbox_row.payload["device_id"] == str(device_id.value)
    assert outbox_row.payload["user_id"] == str(user_id.value)


def test_repeated_registration_does_not_stage_a_second_outbox_event(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    handler = RegisterDeviceHandler(uow, repo)
    command = RegisterDeviceCommand(user_id=UserId.generate(), device_id=DeviceId(uuid.uuid4()))

    handler.handle(command)
    handler.handle(command)

    outbox_rows = session.query(OutboxMessage).filter_by(event_type="DeviceLinked").all()
    assert len(outbox_rows) == 1
