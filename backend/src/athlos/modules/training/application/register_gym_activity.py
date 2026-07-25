"""Use case: register a gym activity."""

from dataclasses import dataclass
from datetime import datetime

from athlos.modules.training.application.ports import GymActivityRepository
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.value_objects import ActivityId, Duration
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId


@dataclass(frozen=True)
class RegisterGymActivityCommand:
    user_id: UserId
    duration_seconds: int
    started_at: datetime


class RegisterGymActivityHandler:
    def __init__(self, uow: UnitOfWork, activities: GymActivityRepository) -> None:
        self._uow = uow
        self._activities = activities

    def handle(self, command: RegisterGymActivityCommand) -> ActivityId:
        activity = GymActivity.register(
            command.user_id, Duration(command.duration_seconds), command.started_at
        )
        self._activities.add(activity)
        self._uow.commit()
        return activity.id
