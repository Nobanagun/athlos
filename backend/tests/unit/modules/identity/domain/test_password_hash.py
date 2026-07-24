"""Tests for the PasswordHash value object."""

from athlos.modules.identity.domain.value_objects import PasswordHash


def test_equal_values_are_equal() -> None:
    assert PasswordHash("$argon2id$abc") == PasswordHash("$argon2id$abc")


def test_different_values_are_not_equal() -> None:
    assert PasswordHash("$argon2id$abc") != PasswordHash("$argon2id$xyz")
