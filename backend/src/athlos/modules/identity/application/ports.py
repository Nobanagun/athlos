"""Repository port for the identity bounded context."""

from abc import ABC, abstractmethod

from athlos.modules.identity.domain.device import Device
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import DeviceId, Email, PasswordHash
from athlos.platform.domain.user_id import UserId


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


class PasswordHasher(ABC):
    """Password hashing/verification port. The concrete algorithm
    (Argon2id) is an infrastructure detail - neither domain nor
    application import it directly (see docs/DECISIONS.md).
    """

    @abstractmethod
    def hash(self, raw_password: str) -> PasswordHash: ...

    @abstractmethod
    def verify(self, raw_password: str, password_hash: PasswordHash) -> bool: ...


class TokenIssuer(ABC):
    """Stateless authentication token issuance/verification port. The
    concrete algorithm (PyJWT/HS256) is an infrastructure detail - kept
    behind this port so it can change without touching domain or
    application (see docs/DECISIONS.md).
    """

    @abstractmethod
    def issue(self, user_id: UserId) -> str: ...

    @abstractmethod
    def verify(self, token: str) -> UserId:
        """Decode and validate `token`, returning the `UserId` it was
        issued for. Raises `InvalidTokenError` if missing, malformed,
        expired, or signed with an unexpected key.
        """
        ...


class DeviceRepository(ABC):
    """Persistence port for `Device`, specific to identity - not a
    generic repository (see docs/DECISIONS.md, Fase 2 entry, for why the
    shared kernel does not provide one).
    """

    @abstractmethod
    def add(self, device: Device) -> None: ...

    @abstractmethod
    def remove(self, device: Device) -> None: ...

    @abstractmethod
    def get_by_user_and_device_id(self, user_id: UserId, device_id: DeviceId) -> Device | None: ...

    @abstractmethod
    def get_by_user(self, user_id: UserId) -> list[Device]: ...
