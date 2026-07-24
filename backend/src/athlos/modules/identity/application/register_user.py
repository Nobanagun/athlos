"""Use case: register a new user."""

from dataclasses import dataclass

from athlos.modules.identity.application.ports import PasswordHasher, UserRepository
from athlos.modules.identity.domain.exceptions import EmailAlreadyRegisteredError, WeakPasswordError
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId

MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str


class RegisterUserHandler:
    """Validates the password strength policy, checks email uniqueness
    (best-effort - see docs/DECISIONS.md for why this is not yet atomic),
    hashes the password, creates the `User`, persists it and commits the
    Unit of Work.
    """

    def __init__(self, uow: UnitOfWork, users: UserRepository, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._users = users
        self._hasher = hasher

    def handle(self, command: RegisterUserCommand) -> UserId:
        email = Email(command.email)
        if len(command.password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError()
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(email)

        password_hash = self._hasher.hash(command.password)
        user = User.register(email, password_hash)
        self._users.add(user)
        self._uow.commit()

        return user.id
