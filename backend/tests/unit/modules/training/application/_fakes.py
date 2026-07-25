"""Test doubles for training application tests - no database involved."""

from athlos.modules.training.application.ports import (
    CyclingActivityRepository,
    GymActivityRepository,
    RunningActivityRepository,
)
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.platform.application.unit_of_work import UnitOfWork
from athlos.platform.domain.user_id import UserId


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1


class InMemoryRunningActivityRepository(RunningActivityRepository):
    def __init__(self) -> None:
        self.activities: list[RunningActivity] = []

    def add(self, activity: RunningActivity) -> None:
        self.activities.append(activity)

    def get_by_user(self, user_id: UserId) -> list[RunningActivity]:
        return [a for a in self.activities if a.user_id == user_id]

    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> RunningActivity | None:
        return next(
            (a for a in self.activities if a.user_id == user_id and a.id == activity_id), None
        )


class InMemoryCyclingActivityRepository(CyclingActivityRepository):
    def __init__(self) -> None:
        self.activities: list[CyclingActivity] = []

    def add(self, activity: CyclingActivity) -> None:
        self.activities.append(activity)

    def get_by_user(self, user_id: UserId) -> list[CyclingActivity]:
        return [a for a in self.activities if a.user_id == user_id]

    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> CyclingActivity | None:
        return next(
            (a for a in self.activities if a.user_id == user_id and a.id == activity_id), None
        )


class InMemoryGymActivityRepository(GymActivityRepository):
    def __init__(self) -> None:
        self.activities: list[GymActivity] = []

    def add(self, activity: GymActivity) -> None:
        self.activities.append(activity)

    def get_by_user(self, user_id: UserId) -> list[GymActivity]:
        return [a for a in self.activities if a.user_id == user_id]

    def get_by_user_and_id(self, user_id: UserId, activity_id: ActivityId) -> GymActivity | None:
        return next(
            (a for a in self.activities if a.user_id == user_id and a.id == activity_id), None
        )
