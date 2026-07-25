"""HTTP routes for the training module.

Endpoints separated by sport, mirroring the independent aggregates and
handlers (see docs/DECISIONS.md) - `GET /activities` is the one
deliberate exception, returning the cross-sport `ActivitySummary`
shape already approved for listing.
"""

import uuid

from fastapi import APIRouter, Depends, status

from athlos.modules.training.application.get_cycling_activity import GetCyclingActivityHandler
from athlos.modules.training.application.get_gym_activity import GetGymActivityHandler
from athlos.modules.training.application.get_running_activity import GetRunningActivityHandler
from athlos.modules.training.application.list_user_activities import ListUserActivitiesHandler
from athlos.modules.training.application.register_cycling_activity import (
    RegisterCyclingActivityCommand,
    RegisterCyclingActivityHandler,
)
from athlos.modules.training.application.register_gym_activity import (
    RegisterGymActivityCommand,
    RegisterGymActivityHandler,
)
from athlos.modules.training.application.register_running_activity import (
    RegisterRunningActivityCommand,
    RegisterRunningActivityHandler,
)
from athlos.modules.training.domain.activity_summary import ActivitySummary
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.modules.training.interfaces.dependencies import (
    get_current_user_id,
    get_get_cycling_activity_handler,
    get_get_gym_activity_handler,
    get_get_running_activity_handler,
    get_list_user_activities_handler,
    get_register_cycling_activity_handler,
    get_register_gym_activity_handler,
    get_register_running_activity_handler,
)
from athlos.modules.training.interfaces.schemas import (
    ActivitySummaryResponse,
    CyclingActivityResponse,
    GymActivityResponse,
    RegisterCyclingActivityRequest,
    RegisterGymActivityRequest,
    RegisterRunningActivityRequest,
    RunningActivityResponse,
)
from athlos.platform.domain.user_id import UserId

router = APIRouter(tags=["training"])


def _running_response(activity: RunningActivity) -> RunningActivityResponse:
    return RunningActivityResponse(
        id=activity.id.value,
        sport=activity.sport.value,
        distance_meters=activity.distance.meters,
        duration_seconds=activity.duration.seconds,
        started_at=activity.started_at,
    )


def _cycling_response(activity: CyclingActivity) -> CyclingActivityResponse:
    return CyclingActivityResponse(
        id=activity.id.value,
        sport=activity.sport.value,
        distance_meters=activity.distance.meters,
        duration_seconds=activity.duration.seconds,
        started_at=activity.started_at,
    )


def _gym_response(activity: GymActivity) -> GymActivityResponse:
    return GymActivityResponse(
        id=activity.id.value,
        sport=activity.sport.value,
        duration_seconds=activity.duration.seconds,
        started_at=activity.started_at,
    )


@router.post("/activities/running", status_code=status.HTTP_201_CREATED)
def register_running_activity(
    request: RegisterRunningActivityRequest,
    user_id: UserId = Depends(get_current_user_id),
    handler: RegisterRunningActivityHandler = Depends(get_register_running_activity_handler),
) -> RunningActivityResponse:
    activity_id = handler.handle(
        RegisterRunningActivityCommand(
            user_id=user_id,
            distance_meters=request.distance_meters,
            duration_seconds=request.duration_seconds,
            started_at=request.started_at,
        )
    )
    return RunningActivityResponse(
        id=activity_id.value,
        sport="running",
        distance_meters=request.distance_meters,
        duration_seconds=request.duration_seconds,
        started_at=request.started_at,
    )


@router.post("/activities/cycling", status_code=status.HTTP_201_CREATED)
def register_cycling_activity(
    request: RegisterCyclingActivityRequest,
    user_id: UserId = Depends(get_current_user_id),
    handler: RegisterCyclingActivityHandler = Depends(get_register_cycling_activity_handler),
) -> CyclingActivityResponse:
    activity_id = handler.handle(
        RegisterCyclingActivityCommand(
            user_id=user_id,
            distance_meters=request.distance_meters,
            duration_seconds=request.duration_seconds,
            started_at=request.started_at,
        )
    )
    return CyclingActivityResponse(
        id=activity_id.value,
        sport="cycling",
        distance_meters=request.distance_meters,
        duration_seconds=request.duration_seconds,
        started_at=request.started_at,
    )


@router.post("/activities/gym", status_code=status.HTTP_201_CREATED)
def register_gym_activity(
    request: RegisterGymActivityRequest,
    user_id: UserId = Depends(get_current_user_id),
    handler: RegisterGymActivityHandler = Depends(get_register_gym_activity_handler),
) -> GymActivityResponse:
    activity_id = handler.handle(
        RegisterGymActivityCommand(
            user_id=user_id,
            duration_seconds=request.duration_seconds,
            started_at=request.started_at,
        )
    )
    return GymActivityResponse(
        id=activity_id.value,
        sport="gym",
        duration_seconds=request.duration_seconds,
        started_at=request.started_at,
    )


@router.get("/activities")
def list_activities(
    user_id: UserId = Depends(get_current_user_id),
    handler: ListUserActivitiesHandler = Depends(get_list_user_activities_handler),
) -> list[ActivitySummaryResponse]:
    def to_summary(activity: ActivitySummary) -> ActivitySummaryResponse:
        return ActivitySummaryResponse(
            id=activity.id.value, sport=activity.sport.value, started_at=activity.started_at
        )

    return [to_summary(activity) for activity in handler.handle(user_id)]


@router.get("/activities/running/{activity_id}")
def get_running_activity(
    activity_id: uuid.UUID,
    user_id: UserId = Depends(get_current_user_id),
    handler: GetRunningActivityHandler = Depends(get_get_running_activity_handler),
) -> RunningActivityResponse:
    return _running_response(handler.handle(user_id, ActivityId(activity_id)))


@router.get("/activities/cycling/{activity_id}")
def get_cycling_activity(
    activity_id: uuid.UUID,
    user_id: UserId = Depends(get_current_user_id),
    handler: GetCyclingActivityHandler = Depends(get_get_cycling_activity_handler),
) -> CyclingActivityResponse:
    return _cycling_response(handler.handle(user_id, ActivityId(activity_id)))


@router.get("/activities/gym/{activity_id}")
def get_gym_activity(
    activity_id: uuid.UUID,
    user_id: UserId = Depends(get_current_user_id),
    handler: GetGymActivityHandler = Depends(get_get_gym_activity_handler),
) -> GymActivityResponse:
    return _gym_response(handler.handle(user_id, ActivityId(activity_id)))
