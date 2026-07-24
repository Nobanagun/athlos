"""Tests for RegisterUserHandler."""

import pytest

from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.domain.exceptions import EmailAlreadyRegisteredError, WeakPasswordError
from athlos.platform.domain.user_id import UserId
from tests.unit.modules.identity.application._fakes import (
    FakePasswordHasher,
    FakeUnitOfWork,
    InMemoryUserRepository,
)


def _handler() -> tuple[RegisterUserHandler, InMemoryUserRepository, FakeUnitOfWork]:
    users = InMemoryUserRepository()
    uow = FakeUnitOfWork()
    return RegisterUserHandler(uow, users, FakePasswordHasher()), users, uow


def test_handle_registers_user_and_returns_its_id() -> None:
    handler, users, uow = _handler()

    result = handler.handle(RegisterUserCommand(email="alice@example.com", password="s3cret!!"))

    assert isinstance(result, UserId)
    assert len(users.add_calls) == 1
    assert users.add_calls[0].id == result
    assert uow.commit_count == 1


def test_handle_stores_a_hash_not_the_raw_password() -> None:
    handler, users, _uow = _handler()

    handler.handle(RegisterUserCommand(email="alice@example.com", password="s3cret!!"))

    assert users.add_calls[0].password_hash.value != "s3cret!!"


def test_handle_rejects_duplicate_email() -> None:
    handler, users, uow = _handler()
    handler.handle(RegisterUserCommand(email="alice@example.com", password="s3cret!!"))

    with pytest.raises(EmailAlreadyRegisteredError):
        handler.handle(RegisterUserCommand(email="alice@example.com", password="s3cret!!"))

    assert len(users.add_calls) == 1
    assert uow.commit_count == 1


def test_handle_rejects_password_shorter_than_eight_characters() -> None:
    handler, users, uow = _handler()

    with pytest.raises(WeakPasswordError):
        handler.handle(RegisterUserCommand(email="alice@example.com", password="short"))

    assert len(users.add_calls) == 0
    assert uow.commit_count == 0
