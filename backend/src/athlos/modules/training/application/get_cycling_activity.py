"""Use case: fetch a single cycling activity owned by the authenticated
user.
"""

from athlos.modules.training.application.ports import CyclingActivityRepository
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.exceptions import ActivityNotFoundError
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.platform.domain.user_id import UserId


class GetCyclingActivityHandler:
    def __init__(self, activities: CyclingActivityRepository) -> None:
        self._activities = activities

    def handle(self, user_id: UserId, activity_id: ActivityId) -> CyclingActivity:
        activity = self._activities.get_by_user_and_id(user_id, activity_id)
        if activity is None:
            raise ActivityNotFoundError()
        return activity
