"""The GymActivity aggregate."""

from datetime import datetime
from typing import ClassVar

from athlos.modules.training.domain.events import ActivityRecorded
from athlos.modules.training.domain.value_objects import ActivityId, Duration, Sport
from athlos.platform.domain.entity import AggregateRoot
from athlos.platform.domain.user_id import UserId


class GymActivity(AggregateRoot[ActivityId]):
    """A recorded gym/strength session. Deliberately minimal for this
    increment - no exercise breakdown (sets/reps/weight); just that a
    session happened and how long it took. Structured exercise tracking
    is a real jump in complexity (sub-entities, a possible exercise
    catalog, per-set validation) with no precedent in the project yet,
    and is not required by `ROADMAP.md`'s Fase 4 criteria - it is left
    for an explicit future increment if a real need shows up (see
    docs/DECISIONS.md).

    No `distance` - unlike `RunningActivity`/`CyclingActivity`.
    """

    sport: ClassVar[Sport] = Sport.GYM

    def __init__(
        self, id: ActivityId, user_id: UserId, duration: Duration, started_at: datetime
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.duration = duration
        self.started_at = started_at

    @classmethod
    def register(cls, user_id: UserId, duration: Duration, started_at: datetime) -> "GymActivity":
        activity = cls(
            id=ActivityId.generate(), user_id=user_id, duration=duration, started_at=started_at
        )
        activity.record_event(
            ActivityRecorded(
                activity_id=str(activity.id.value),
                user_id=str(user_id.value),
                sport=cls.sport.value,
            )
        )
        return activity
