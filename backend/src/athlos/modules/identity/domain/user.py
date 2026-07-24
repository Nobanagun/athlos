"""The User aggregate."""

from enum import Enum

from athlos.modules.identity.domain.events import UserRegistered
from athlos.modules.identity.domain.value_objects import Email, PasswordHash, UserId
from athlos.platform.domain.entity import AggregateRoot


class AccountStatus(Enum):
    """Account status. Only `ACTIVE` exists for now - no use case yet
    transitions an account to any other state; more values are added only
    once a real use case needs them.
    """

    ACTIVE = "active"


class User(AggregateRoot[UserId]):
    """A registered user. `register()` is the sole intended entry point
    for creating new users - `__init__` stays public (Python has no real
    private constructors), but callers should not construct a `User`
    directly.
    """

    def __init__(
        self, id: UserId, email: Email, password_hash: PasswordHash, status: AccountStatus
    ) -> None:
        super().__init__(id)
        self.email = email
        self.password_hash = password_hash
        self.status = status

    @classmethod
    def register(cls, email: Email, password_hash: PasswordHash) -> "User":
        """`password_hash` arrives already hashed - hashing is an
        application-layer concern via the `PasswordHasher` port; `User`
        never sees a raw password or hashing algorithm (see
        docs/DECISIONS.md).
        """
        user = cls(
            id=UserId.generate(),
            email=email,
            password_hash=password_hash,
            status=AccountStatus.ACTIVE,
        )
        user.record_event(UserRegistered(user_id=str(user.id.value), email=email.value))
        return user
