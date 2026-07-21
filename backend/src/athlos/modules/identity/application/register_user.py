"""Use case: register a new user."""

from dataclasses import dataclass

from athlos.modules.identity.application.ports import UserRepository
from athlos.modules.identity.domain.exceptions import EmailAlreadyRegisteredError
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email, UserId
from athlos.platform.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str


class RegisterUserHandler:
    """Checks email uniqueness (best-effort - see docs/DECISIONS.md for
    why this is not yet atomic), creates the `User`, persists it and
    commits the Unit of Work.
    """

    def __init__(self, uow: UnitOfWork, users: UserRepository) -> None:
        self._uow = uow
        self._users = users

    def handle(self, command: RegisterUserCommand) -> UserId:
        email = Email(command.email)
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(email)

        user = User.register(email)
        self._users.add(user)
        self._uow.commit()

        return user.id
