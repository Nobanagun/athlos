"""Tests for the Email value object."""

import pytest

from athlos.modules.identity.domain.exceptions import InvalidEmailError
from athlos.modules.identity.domain.value_objects import Email


def test_email_is_normalized_to_lowercase_and_trimmed() -> None:
    assert Email("  Alice@Example.COM  ").value == "alice@example.com"


def test_equal_emails_after_normalization_are_equal() -> None:
    assert Email("Alice@Example.com") == Email("alice@example.com")


@pytest.mark.parametrize(
    "invalid",
    ["", "no-at-sign", "@example.com", "alice@", "a@b@example.com"],
)
def test_invalid_email_raises(invalid: str) -> None:
    with pytest.raises(InvalidEmailError, match="Invalid email"):
        Email(invalid)
