"""Identity of a user - a cross-cutting concept in the shared kernel.

`UserId` used to live in `identity/domain`, but "who owns this record" is
not specific to the `identity` bounded context: every module with
user-owned data (`training`, `recovery`, `planning`, ...) needs to
reference it without depending on `identity`'s domain layer, which
`ARCHITECTURE.md`'s module boundary rule does not allow (see
docs/DECISIONS.md).
"""

import uuid
from dataclasses import dataclass

from athlos.platform.domain.value_object import ValueObject


@dataclass(frozen=True)
class UserId(ValueObject):
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "UserId":
        return cls(uuid.uuid4())
