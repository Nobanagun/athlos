"""Use case: register a running activity."""

from dataclasses import dataclass
from datetime import datetime

from athlos.modules.training.application.ports import RunningActivityRepository
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId, Distance, Duration
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId


@dataclass(frozen=True)
class RegisterRunningActivityCommand:
    user_id: UserId
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class RegisterRunningActivityHandler:
    def __init__(self, uow: UnitOfWork, activities: RunningActivityRepository) -> None:
        self._uow = uow
        self._activities = activities

    def handle(self, command: RegisterRunningActivityCommand) -> ActivityId:
        activity = RunningActivity.register(
            command.user_id,
            Distance(command.distance_meters),
            Duration(command.duration_seconds),
            command.started_at,
        )
        self._activities.add(activity)
        self._uow.commit()
        return activity.id
