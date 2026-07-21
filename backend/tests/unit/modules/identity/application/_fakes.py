"""Test doubles for identity application tests - no database involved."""

from athlos.modules.identity.application.ports import UserRepository
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email, UserId
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
