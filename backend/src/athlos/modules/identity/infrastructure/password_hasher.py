"""Argon2id-backed implementation of the `PasswordHasher` port."""

from argon2 import PasswordHasher as _Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from athlos.modules.identity.application.ports import PasswordHasher
from athlos.modules.identity.domain.value_objects import PasswordHash


class Argon2PasswordHasher(PasswordHasher):
    """Uses argon2-cffi's default parameters, which hash with Argon2id -
    no custom tuning in this increment (see docs/DECISIONS.md)."""

    def __init__(self) -> None:
        self._hasher = _Argon2PasswordHasher()

    def hash(self, raw_password: str) -> PasswordHash:
        return PasswordHash(self._hasher.hash(raw_password))

    def verify(self, raw_password: str, password_hash: PasswordHash) -> bool:
        try:
            self._hasher.verify(password_hash.value, raw_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
        return True
