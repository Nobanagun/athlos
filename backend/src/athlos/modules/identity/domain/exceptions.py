"""Domain-rule violations for the identity bounded context."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from athlos.modules.identity.domain.value_objects import Email


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register a user with an email already in use."""

    def __init__(self, email: "Email") -> None:
        super().__init__(f"Email already registered: {email.value}")
        self.email = email


class InvalidEmailError(Exception):
    """Raised when an email fails `Email`'s structural validation.

    Deliberately not a subclass of `ValueError`: the HTTP layer needs to
    catch this specifically, and a bare `ValueError` is too broad to
    catch safely (see docs/DECISIONS.md).
    """

    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid email: {value!r}")
        self.value = value


class WeakPasswordError(Exception):
    """Raised when a candidate password fails the minimum strength policy
    enforced by the application layer (see docs/DECISIONS.md - a domain
    exception, not a Pydantic field constraint, so the rule is a real
    business invariant rather than HTTP-layer input formatting).
    """

    def __init__(self) -> None:
        super().__init__("Password must be at least 8 characters long.")


class InvalidCredentialsError(Exception):
    """Raised on login failure.

    Deliberately generic: does not distinguish "no user with this email"
    from "wrong password", to avoid leaking which emails are registered
    (user enumeration).
    """

    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class InvalidTokenError(Exception):
    """Raised when a bearer token is missing, malformed, expired, or
    signed with an unexpected key - or when it verifies but no longer
    resolves to an existing user.
    """

    def __init__(self) -> None:
        super().__init__("Invalid or expired authentication token.")
