"""End-to-end test: UnlinkDeviceHandler wired with the real repository
and the real Unit of Work - no test doubles anywhere in this file.

First real exercise, in this codebase, of `SqlAlchemyUnitOfWork` staging
an outbox event for a *deleted* aggregate (`session.deleted`, not
`session.new`/`session.dirty`) - see docs/DECISIONS.md.
"""

import uuid

from sqlalchemy.orm import Session

from athlos.modules.identity.application.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceHandler,
)
from athlos.modules.identity.application.unlink_device import (
    UnlinkDeviceCommand,
    UnlinkDeviceHandler,
)
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.modules.identity.infrastructure.device_repository import SqlAlchemyDeviceRepository
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_unlink_device_removes_it_and_stages_outbox_event(session: Session) -> None:
    repo = SqlAlchemyDeviceRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    user_id = UserId.generate()
    device_id = DeviceId(uuid.uuid4())
    RegisterDeviceHandler(uow, repo).handle(
        RegisterDeviceCommand(user_id=user_id, device_id=device_id)
    )

    UnlinkDeviceHandler(uow, repo).handle(UnlinkDeviceCommand(user_id=user_id, device_id=device_id))

    assert repo.get_by_user_and_device_id(user_id, device_id) is None

    outbox_row = session.query(OutboxMessage).filter_by(event_type="DeviceUnlinked").one()
    assert outbox_row.processed_at is None
    assert outbox_row.payload["device_id"] == str(device_id.value)
    assert outbox_row.payload["user_id"] == str(user_id.value)
