"""Use case: register a cycling activity."""

from dataclasses import dataclass
from datetime import datetime

from athlos.modules.training.application.ports import CyclingActivityRepository
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId


@dataclass(frozen=True)
class RegisterCyclingActivityCommand:
    user_id: UserId
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class RegisterCyclingActivityHandler:
    def __init__(self, uow: UnitOfWork, activities: CyclingActivityRepository) -> None:
        self._uow = uow
        self._activities = activities

    def handle(self, command: RegisterCyclingActivityCommand) -> ActivityId:
        activity = CyclingActivity.register(
            command.user_id,
            Distance(command.distance_meters),
            Duration(command.duration_seconds),
            command.started_at,
        )
        self._activities.add(activity)
        self._uow.commit()
        return activity.id
