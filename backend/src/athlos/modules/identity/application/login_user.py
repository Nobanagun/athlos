"""Use case: authenticate a user and issue a stateless access token."""

from dataclasses import dataclass

from athlos.modules.identity.application.ports import PasswordHasher, TokenIssuer, UserRepository
from athlos.modules.identity.domain.exceptions import InvalidCredentialsError
from athlos.modules.identity.domain.value_objects import Email


@dataclass(frozen=True)
class LoginUserCommand:
    email: str
    password: str


class LoginUserHandler:
    """Verifies credentials and issues a JWT. Read-only - no Unit of Work,
    since a successful login does not change any persisted state (see
    docs/DECISIONS.md - stateless auth, no session/refresh-token storage
    in this increment).
    """

    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenIssuer) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def handle(self, command: LoginUserCommand) -> str:
        email = Email(command.email)
        user = self._users.get_by_email(email)
        if user is None or not self._hasher.verify(command.password, user.password_hash):
            raise InvalidCredentialsError()

        return self._tokens.issue(user.id)
