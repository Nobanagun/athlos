"""End-to-end test: RegisterUserHandler wired with the real repository
and the real Unit of Work - no test doubles anywhere in this file.
"""

import pytest
from sqlalchemy.orm import Session

from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.domain.exceptions import EmailAlreadyRegisteredError
from athlos.modules.identity.domain.user import AccountStatus
from athlos.modules.identity.domain.value_objects import Email
from athlos.modules.identity.infrastructure.password_hasher import Argon2PasswordHasher
from athlos.modules.identity.infrastructure.repository import SqlAlchemyUserRepository
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_register_user_persists_and_stages_outbox_event(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    handler = RegisterUserHandler(uow, repo, Argon2PasswordHasher())

    result = handler.handle(RegisterUserCommand(email="carol@example.com", password="s3cret!!"))

    assert isinstance(result, UserId)

    persisted = repo.get_by_id(result)
    assert persisted is not None
    assert persisted.email.value == "carol@example.com"
    assert persisted.password_hash.value != "s3cret!!"
    assert persisted.status is AccountStatus.ACTIVE

    outbox_row = session.query(OutboxMessage).filter_by(event_type="UserRegistered").one()
    assert outbox_row.processed_at is None
    assert outbox_row.payload == {
        "user_id": str(result.value),
        "email": "carol@example.com",
    }


def test_register_duplicate_email_raises_and_persists_nothing(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    handler = RegisterUserHandler(uow, repo, Argon2PasswordHasher())
    first_id = handler.handle(RegisterUserCommand(email="dana@example.com", password="s3cret!!"))

    with pytest.raises(EmailAlreadyRegisteredError):
        handler.handle(RegisterUserCommand(email="dana@example.com", password="s3cret!!"))

    # Still only the first user - the second attempt never reached add()/commit().
    found = repo.get_by_email(Email("dana@example.com"))
    assert found is not None
    assert found.id == first_id

    outbox_rows = session.query(OutboxMessage).filter_by(event_type="UserRegistered").all()
    assert len(outbox_rows) == 1
