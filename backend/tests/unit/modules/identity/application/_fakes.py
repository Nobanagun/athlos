"""Test doubles for identity application tests - no database involved."""

import uuid

from athlos.modules.identity.application.ports import PasswordHasher, TokenIssuer, UserRepository
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email, PasswordHash, UserId
from athlos.platform.application.unit_of_work import UnitOfWork


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[UserId, User] = {}
        self.add_calls: list[User] = []

    def add(self, user: User) -> None:
        self.users[user.id] = user
        self.add_calls.append(user)

    def get_by_id(self, user_id: UserId) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: Email) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)


class FakeUnitOfWork(UnitOfWork):
    """Counts commit()/rollback() calls, without touching any database -
    the identity application layer is tested in isolation from the shared
    kernel's SQLAlchemy implementation.
    """

    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1


class FakePasswordHasher(PasswordHasher):
    """Deterministic, insecure "hashing" (reversed string) - fine for
    tests, never used outside them. Avoids depending on the real Argon2id
    adapter (infrastructure) from pure application-layer tests.
    """

    def hash(self, raw_password: str) -> PasswordHash:
        return PasswordHash(raw_password[::-1])

    def verify(self, raw_password: str, password_hash: PasswordHash) -> bool:
        return raw_password[::-1] == password_hash.value


class FakeTokenIssuer(TokenIssuer):
    """Issues the user id itself as the "token" - no real JWT involved,
    keeping application-layer tests independent of the PyJWT adapter.
    """

    def __init__(self) -> None:
        self.issued_for: list[UserId] = []

    def issue(self, user_id: UserId) -> str:
        self.issued_for.append(user_id)
        return str(user_id.value)

    def verify(self, token: str) -> UserId:
        return UserId(uuid.UUID(token))
