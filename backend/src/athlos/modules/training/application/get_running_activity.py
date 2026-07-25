"""Use case: fetch a single running activity owned by the authenticated
user.
"""

from athlos.modules.training.application.ports import RunningActivityRepository
from athlos.modules.training.domain.exceptions import ActivityNotFoundError
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.platform.domain.user_id import UserId


class GetRunningActivityHandler:
    def __init__(self, activities: RunningActivityRepository) -> None:
        self._activities = activities

    def handle(self, user_id: UserId, activity_id: ActivityId) -> RunningActivity:
        activity = self._activities.get_by_user_and_id(user_id, activity_id)
        if activity is None:
            raise ActivityNotFoundError()
        return activity
