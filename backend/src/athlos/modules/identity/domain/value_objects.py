"""Value objects for the identity bounded context."""

import uuid
from dataclasses import dataclass

from athlos.platform.domain.value_object import ValueObject


@dataclass(frozen=True)
class UserId(ValueObject):
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "UserId":
        return cls(uuid.uuid4())


@dataclass(frozen=True)
class Email(ValueObject):
    """An email address, normalized and structurally validated.

    Validation is deliberately minimal (no external library): normalizes
    with `strip()` + `lower()` first, then checks for exactly one `@` with
    non-empty local and domain parts. Stricter validation (or a dedicated
    library) can be added later if real-world input demands it.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        local, _, domain = normalized.partition("@")
        if not local or not domain or "@" in domain:
            raise ValueError(f"Invalid email: {self.value!r}")
        object.__setattr__(self, "value", normalized)
