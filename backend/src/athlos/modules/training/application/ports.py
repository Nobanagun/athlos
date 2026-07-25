"""Repository ports for the training bounded context.

Three separate ports, not one generic `ActivityRepository[T]` - mirrors
the independence of the three aggregates (see docs/DECISIONS.md): a
generic repository would have to either use a union type or an
`isinstance` dispatch internally, exactly the coupling the
independent-aggregates decision was meant to avoid.
"""

from abc import ABC, abstractmethod

from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.platform.domain.user_id import UserId


class RunningActivityRepository(ABC):
    @abstractmethod
    def add(self, activity: RunningActivity) -> None: ...

    @abstractmethod
    def get_by_user(self, user_id: UserId) -> list[RunningActivity]: ...

    @abstractmethod
    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> RunningActivity | None: ...


class CyclingActivityRepository(ABC):
    @abstractmethod
    def add(self, activity: CyclingActivity) -> None: ...

    @abstractmethod
    def get_by_user(self, user_id: UserId) -> list[CyclingActivity]: ...

    @abstractmethod
    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> CyclingActivity | None: ...


class GymActivityRepository(ABC):
    @abstractmethod
    def add(self, activity: GymActivity) -> None: ...

    @abstractmethod
    def get_by_user(self, user_id: UserId) -> list[GymActivity]: ...

    @abstractmethod
    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> GymActivity | None: ...
