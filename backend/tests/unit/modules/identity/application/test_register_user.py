"""Tests for RegisterUserHandler."""

import pytest

from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.domain.exceptions import EmailAlreadyRegisteredError
from athlos.modules.identity.domain.value_objects import UserId
from tests.unit.modules.identity.application._fakes import (
    FakeUnitOfWork,
    InMemoryUserRepository,
)


def test_handle_registers_user_and_returns_its_id() -> None:
    users = InMemoryUserRepository()
    uow = FakeUnitOfWork()
    handler = RegisterUserHandler(uow, users)

    result = handler.handle(RegisterUserCommand(email="alice@example.com"))

    assert isinstance(result, UserId)
    assert len(users.add_calls) == 1
    assert users.add_calls[0].id == result
    assert uow.commit_count == 1


def test_handle_rejects_duplicate_email() -> None:
    users = InMemoryUserRepository()
    uow = FakeUnitOfWork()
    handler = RegisterUserHandler(uow, users)
    handler.handle(RegisterUserCommand(email="alice@example.com"))

    with pytest.raises(EmailAlreadyRegisteredError):
        handler.handle(RegisterUserCommand(email="alice@example.com"))

    assert len(users.add_calls) == 1
    assert uow.commit_count == 1
