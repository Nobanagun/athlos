"""FastAPI dependencies specific to the training module.

Authentication is not reimplemented here - every route depends on
`identity.interfaces.dependencies.get_current_user_id`, the same
cross-cutting mechanism `identity`'s own protected routes use. This is
not a domain coupling (training does not import identity's domain or
repositories) - it is using the one shared HTTP auth mechanism, the
same way any future protected module will.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from athlos.api.dependencies import get_session, get_unit_of_work
from athlos.modules.identity.interfaces.dependencies import get_current_user_id
from athlos.modules.training.application.get_cycling_activity import GetCyclingActivityHandler
from athlos.modules.training.application.get_gym_activity import GetGymActivityHandler
from athlos.modules.training.application.get_running_activity import GetRunningActivityHandler
from athlos.modules.training.application.list_user_activities import ListUserActivitiesHandler
from athlos.modules.training.application.ports import (
    CyclingActivityRepository,
    GymActivityRepository,
    RunningActivityRepository,
)
from athlos.modules.training.application.register_cycling_activity import (
    RegisterCyclingActivityHandler,
)
from athlos.modules.training.application.register_gym_activity import RegisterGymActivityHandler
from athlos.modules.training.application.register_running_activity import (
    RegisterRunningActivityHandler,
)
from athlos.modules.training.infrastructure.cycling_repository import (
    SqlAlchemyCyclingActivityRepository,
)
from athlos.modules.training.infrastructure.gym_repository import SqlAlchemyGymActivityRepository
from athlos.modules.training.infrastructure.running_repository import (
    SqlAlchemyRunningActivityRepository,
)
from athlos.platform.application.unit_of_work import UnitOfWork

# Re-exported so routes.py has a single import for the auth dependency,
# without needing to know it lives in identity's interfaces.
__all__ = ["get_current_user_id"]


def get_running_activity_repository(
    session: Session = Depends(get_session),
) -> RunningActivityRepository:
    return SqlAlchemyRunningActivityRepository(session)


def get_cycling_activity_repository(
    session: Session = Depends(get_session),
) -> CyclingActivityRepository:
    return SqlAlchemyCyclingActivityRepository(session)


def get_gym_activity_repository(session: Session = Depends(get_session)) -> GymActivityRepository:
    return SqlAlchemyGymActivityRepository(session)


def get_register_running_activity_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    activities: RunningActivityRepository = Depends(get_running_activity_repository),
) -> RegisterRunningActivityHandler:
    return RegisterRunningActivityHandler(uow, activities)


def get_register_cycling_activity_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    activities: CyclingActivityRepository = Depends(get_cycling_activity_repository),
) -> RegisterCyclingActivityHandler:
    return RegisterCyclingActivityHandler(uow, activities)


def get_register_gym_activity_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    activities: GymActivityRepository = Depends(get_gym_activity_repository),
) -> RegisterGymActivityHandler:
    return RegisterGymActivityHandler(uow, activities)


def get_get_running_activity_handler(
    activities: RunningActivityRepository = Depends(get_running_activity_repository),
) -> GetRunningActivityHandler:
    return GetRunningActivityHandler(activities)


def get_get_cycling_activity_handler(
    activities: CyclingActivityRepository = Depends(get_cycling_activity_repository),
) -> GetCyclingActivityHandler:
    return GetCyclingActivityHandler(activities)


def get_get_gym_activity_handler(
    activities: GymActivityRepository = Depends(get_gym_activity_repository),
) -> GetGymActivityHandler:
    return GetGymActivityHandler(activities)


def get_list_user_activities_handler(
    running: RunningActivityRepository = Depends(get_running_activity_repository),
    cycling: CyclingActivityRepository = Depends(get_cycling_activity_repository),
    gym: GymActivityRepository = Depends(get_gym_activity_repository),
) -> ListUserActivitiesHandler:
    return ListUserActivitiesHandler(running, cycling, gym)
