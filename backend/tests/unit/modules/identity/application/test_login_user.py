"""Tests for LoginUserHandler."""

import pytest

from athlos.modules.identity.application.login_user import LoginUserCommand, LoginUserHandler
from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.domain.exceptions import InvalidCredentialsError
from tests.unit.modules.identity.application._fakes import (
    FakePasswordHasher,
    FakeTokenIssuer,
    FakeUnitOfWork,
    InMemoryUserRepository,
)


def _registered_user(users: InMemoryUserRepository, hasher: FakePasswordHasher) -> None:
    RegisterUserHandler(FakeUnitOfWork(), users, hasher).handle(
        RegisterUserCommand(email="alice@example.com", password="s3cret!!")
    )


def test_handle_returns_a_token_for_correct_credentials() -> None:
    users = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    _registered_user(users, hasher)
    tokens = FakeTokenIssuer()
    handler = LoginUserHandler(users, hasher, tokens)

    token = handler.handle(LoginUserCommand(email="alice@example.com", password="s3cret!!"))

    assert token == str(tokens.issued_for[0].value)


def test_handle_rejects_wrong_password() -> None:
    users = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    _registered_user(users, hasher)
    handler = LoginUserHandler(users, hasher, FakeTokenIssuer())

    with pytest.raises(InvalidCredentialsError):
        handler.handle(LoginUserCommand(email="alice@example.com", password="wrong-password"))


def test_handle_rejects_unknown_email() -> None:
    users = InMemoryUserRepository()
    handler = LoginUserHandler(users, FakePasswordHasher(), FakeTokenIssuer())

    with pytest.raises(InvalidCredentialsError):
        handler.handle(LoginUserCommand(email="nobody@example.com", password="whatever1"))


def test_unknown_email_and_wrong_password_raise_the_same_generic_error() -> None:
    """Both failure modes must be indistinguishable to the caller - see
    docs/DECISIONS.md on avoiding user enumeration via login errors.
    """
    users = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    _registered_user(users, hasher)
    handler = LoginUserHandler(users, hasher, FakeTokenIssuer())

    with pytest.raises(InvalidCredentialsError) as unknown_email_exc:
        handler.handle(LoginUserCommand(email="nobody@example.com", password="whatever1"))
    with pytest.raises(InvalidCredentialsError) as wrong_password_exc:
        handler.handle(LoginUserCommand(email="alice@example.com", password="wrong-password"))

    assert str(unknown_email_exc.value) == str(wrong_password_exc.value)
