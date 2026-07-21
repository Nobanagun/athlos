"""Domain-rule violations for the identity bounded context."""

from athlos.modules.identity.domain.value_objects import Email


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register a user with an email already in use."""

    def __init__(self, email: Email) -> None:
        super().__init__(f"Email already registered: {email.value}")
        self.email = email
