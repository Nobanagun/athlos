"""ORM mapping for the training bounded context.

Three separate tables, one per sport - consequence of the three
aggregates being fully independent (see docs/DECISIONS.md), same
`_MappedX` + `TypeDecorator` pattern already used twice in `identity`.
"""

import uuid
from datetime import datetime

from sqlalchemy import Float, Integer, TypeDecorator, Uuid
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column

from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration
from athlos.platform.domain.user_id import UserId
from athlos.platform.infrastructure.persistence.database import Base
from athlos.platform.infrastructure.persistence.utc_datetime import UtcDateTimeType


class ActivityIdType(TypeDecorator[ActivityId]):
    """Persists an `ActivityId` value object as its underlying `uuid.UUID`."""

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value: ActivityId | None, dialect: Dialect) -> uuid.UUID | None:
        return value.value if value is not None else None

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> ActivityId | None:
        return ActivityId(value) if value is not None else None


class UserIdType(TypeDecorator[UserId]):
    """Persists a `UserId` value object as its underlying `uuid.UUID`.

    Same shape as `identity/infrastructure/models.py`'s `UserIdType` -
    not shared as code because a `TypeDecorator` is infrastructure
    wiring specific to each module's own ORM models, not a concept
    `UserId` itself needs to expose (see docs/DECISIONS.md, `UserId`
    promotion entry).
    """

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value: UserId | None, dialect: Dialect) -> uuid.UUID | None:
        return value.value if value is not None else None

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> UserId | None:
        return UserId(value) if value is not None else None


class DurationType(TypeDecorator[Duration]):
    """Persists a `Duration` value object as its underlying `int` seconds."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Duration | None, dialect: Dialect) -> int | None:
        return value.seconds if value is not None else None

    def process_result_value(self, value: int | None, dialect: Dialect) -> Duration | None:
        return Duration(value) if value is not None else None


class DistanceType(TypeDecorator[Distance]):
    """Persists a `Distance` value object as its underlying `float` meters."""

    impl = Float
    cache_ok = True

    def process_bind_param(self, value: Distance | None, dialect: Dialect) -> float | None:
        return value.meters if value is not None else None

    def process_result_value(self, value: float | None, dialect: Dialect) -> Distance | None:
        return Distance(value) if value is not None else None


class _MappedRunningActivity(RunningActivity, Base):
    """Private ORM mapping of `RunningActivity` - never import outside
    `training/infrastructure/`. `RunningActivity` first in the base
    list, same convention as `_MappedUser`/`_MappedDevice`.
    """

    __tablename__ = "running_activities"

    id: Mapped[ActivityId] = mapped_column(ActivityIdType, primary_key=True)
    user_id: Mapped[UserId] = mapped_column(UserIdType, nullable=False)
    distance: Mapped[Distance] = mapped_column(DistanceType, nullable=False)
    duration: Mapped[Duration] = mapped_column(DurationType, nullable=False)
    started_at: Mapped[datetime] = mapped_column(UtcDateTimeType, nullable=False)

    @classmethod
    def from_domain(cls, activity: RunningActivity) -> "_MappedRunningActivity":
        mapped = cls(
            id=activity.id,
            user_id=activity.user_id,
            distance=activity.distance,
            duration=activity.duration,
            started_at=activity.started_at,
        )
        for event in activity.domain_events:
            mapped.record_event(event)
        return mapped


class _MappedCyclingActivity(CyclingActivity, Base):
    """Private ORM mapping of `CyclingActivity`."""

    __tablename__ = "cycling_activities"

    id: Mapped[ActivityId] = mapped_column(ActivityIdType, primary_key=True)
    user_id: Mapped[UserId] = mapped_column(UserIdType, nullable=False)
    distance: Mapped[Distance] = mapped_column(DistanceType, nullable=False)
    duration: Mapped[Duration] = mapped_column(DurationType, nullable=False)
    started_at: Mapped[datetime] = mapped_column(UtcDateTimeType, nullable=False)

    @classmethod
    def from_domain(cls, activity: CyclingActivity) -> "_MappedCyclingActivity":
        mapped = cls(
            id=activity.id,
            user_id=activity.user_id,
            distance=activity.distance,
            duration=activity.duration,
            started_at=activity.started_at,
        )
        for event in activity.domain_events:
            mapped.record_event(event)
        return mapped


class _MappedGymActivity(GymActivity, Base):
    """Private ORM mapping of `GymActivity` - no `distance` column,
    unlike the other two.
    """

    __tablename__ = "gym_activities"

    id: Mapped[ActivityId] = mapped_column(ActivityIdType, primary_key=True)
    user_id: Mapped[UserId] = mapped_column(UserIdType, nullable=False)
    duration: Mapped[Duration] = mapped_column(DurationType, nullable=False)
    started_at: Mapped[datetime] = mapped_column(UtcDateTimeType, nullable=False)

    @classmethod
    def from_domain(cls, activity: GymActivity) -> "_MappedGymActivity":
        mapped = cls(
            id=activity.id,
            user_id=activity.user_id,
            duration=activity.duration,
            started_at=activity.started_at,
        )
        for event in activity.domain_events:
            mapped.record_event(event)
        return mapped
