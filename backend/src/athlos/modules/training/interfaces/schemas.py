"""Pydantic request/response models for the training HTTP interface.

DTOs live only here - `training/domain` and `training/application`
never import Pydantic.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class RegisterRunningActivityRequest(BaseModel):
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class RegisterCyclingActivityRequest(BaseModel):
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class RegisterGymActivityRequest(BaseModel):
    duration_seconds: int
    started_at: datetime


class RunningActivityResponse(BaseModel):
    id: uuid.UUID
    sport: str
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class CyclingActivityResponse(BaseModel):
    id: uuid.UUID
    sport: str
    distance_meters: float
    duration_seconds: int
    started_at: datetime


class GymActivityResponse(BaseModel):
    id: uuid.UUID
    sport: str
    duration_seconds: int
    started_at: datetime


class ActivitySummaryResponse(BaseModel):
    """Shape of `GET /activities` (cross-sport list) - mirrors the
    `ActivitySummary` domain contract exactly: only the fields already
    approved as common (see docs/DECISIONS.md).
    """

    id: uuid.UUID
    sport: str
    started_at: datetime
