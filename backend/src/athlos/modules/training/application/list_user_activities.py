"""Use case: list the authenticated user's activities, across sports."""

from athlos.modules.training.application.ports import (
    CyclingActivityRepository,
    GymActivityRepository,
    RunningActivityRepository,
)
from athlos.modules.training.domain.activity_summary import ActivitySummary
from athlos.platform.domain.user_id import UserId


class ListUserActivitiesHandler:
    """Read-only - no `UnitOfWork`, same criterion as `identity`'s
    `ListUserDevicesHandler`. Orchestrates the three repositories and
    merges in Python rather than a dedicated read-model/projection -
    the simpler option for the data volume of this increment (see
    docs/DECISIONS.md); revisit if it ever becomes a real bottleneck.
    """

    def __init__(
        self,
        running: RunningActivityRepository,
        cycling: CyclingActivityRepository,
        gym: GymActivityRepository,
    ) -> None:
        self._running = running
        self._cycling = cycling
        self._gym = gym

    def handle(self, user_id: UserId) -> list[ActivitySummary]:
        activities: list[ActivitySummary] = [
            *self._running.get_by_user(user_id),
            *self._cycling.get_by_user(user_id),
            *self._gym.get_by_user(user_id),
        ]
        return sorted(activities, key=lambda activity: activity.started_at, reverse=True)
