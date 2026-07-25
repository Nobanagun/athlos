"""Structural contract shared by the three activity aggregates.

Deliberately minimal - only the fields already approved as common (see
docs/DECISIONS.md): `id`, `user_id`, `sport`, `started_at`. Nothing
else is shared; `RunningActivity`/`CyclingActivity`/`GymActivity` stay
otherwise completely independent aggregates, each with its own fields
and invariants. A `Protocol`, not a base class - no inheritance between
the three aggregates.
"""

from datetime import datetime
from typing import Protocol

from athlos.modules.training.domain.value_objects import ActivityId, Sport
from athlos.platform.domain.user_id import UserId


class ActivitySummary(Protocol):
    @property
    def id(self) -> ActivityId: ...

    @property
    def user_id(self) -> UserId: ...

    @property
    def sport(self) -> Sport: ...

    @property
    def started_at(self) -> datetime: ...
