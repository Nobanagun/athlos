"""Tests for the Argon2id-backed PasswordHasher adapter - no database
involved.
"""

from athlos.modules.identity.domain.value_objects import PasswordHash
from athlos.modules.identity.infrastructure.password_hasher import Argon2PasswordHasher


def test_hash_does_not_return_the_raw_password() -> None:
    hasher = Argon2PasswordHasher()

    result = hasher.hash("correct horse battery staple")

    assert result.value != "correct horse battery staple"
    assert result.value.startswith("$argon2id$")


def test_verify_accepts_the_correct_password() -> None:
    hasher = Argon2PasswordHasher()
    password_hash = hasher.hash("correct horse battery staple")

    assert hasher.verify("correct horse battery staple", password_hash) is True


def test_verify_rejects_the_wrong_password() -> None:
    hasher = Argon2PasswordHasher()
    password_hash = hasher.hash("correct horse battery staple")

    assert hasher.verify("wrong password", password_hash) is False


def test_verify_rejects_a_malformed_hash_instead_of_raising() -> None:
    hasher = Argon2PasswordHasher()

    assert hasher.verify("anything", PasswordHash("not-a-real-hash")) is False


def test_two_hashes_of_the_same_password_are_not_equal() -> None:
    """Argon2id salts each hash - two calls must not be comparable
    directly, only via `verify()`.
    """
    hasher = Argon2PasswordHasher()

    first = hasher.hash("correct horse battery staple")
    second = hasher.hash("correct horse battery staple")

    assert first.value != second.value
