"""The RunningActivity aggregate."""

from datetime import datetime
from typing import ClassVar

from athlos.modules.training.domain.events import ActivityRecorded
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration, Sport
from athlos.platform.domain.entity import AggregateRoot
from athlos.platform.domain.user_id import UserId


class RunningActivity(AggregateRoot[ActivityId]):
    """A recorded running session. `register()` is the sole intended
    entry point - `__init__` stays public (Python has no real private
    constructors), but callers should not construct one directly.

    Independent from `CyclingActivity`/`GymActivity` - no shared base
    class, no shared table, only the same identity *type* (`ActivityId`)
    and the structural `ActivitySummary` contract (see docs/DECISIONS.md).
    """

    sport: ClassVar[Sport] = Sport.RUNNING

    def __init__(
        self,
        id: ActivityId,
        user_id: UserId,
        distance: Distance,
        duration: Duration,
        started_at: datetime,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.distance = distance
        self.duration = duration
        self.started_at = started_at

    @classmethod
    def register(
        cls, user_id: UserId, distance: Distance, duration: Duration, started_at: datetime
    ) -> "RunningActivity":
        activity = cls(
            id=ActivityId.generate(),
            user_id=user_id,
            distance=distance,
            duration=duration,
            started_at=started_at,
        )
        activity.record_event(
            ActivityRecorded(
                activity_id=str(activity.id.value),
                user_id=str(user_id.value),
                sport=cls.sport.value,
            )
        )
        return activity
