"""Repository port for the identity bounded context."""

from abc import ABC, abstractmethod

from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email, UserId


class UserRepository(ABC):
    """Persistence port for `User`, specific to identity - not a generic
    repository (see docs/DECISIONS.md, Fase 2 entry, for why the shared
    kernel does not provide one).
    """

    @abstractmethod
    def add(self, user: User) -> None: ...

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: Email) -> User | None: ...
