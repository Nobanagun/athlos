"""Value objects and shared enums for the training bounded context.

Units are always SI (meters, seconds) - unit conversion for display
(miles, feet, ...) is a mobile presentation concern, never a domain one
(see docs/DECISIONS.md).
"""

import uuid
from dataclasses import dataclass
from enum import Enum

from athlos.modules.training.domain.exceptions import InvalidDistanceError, InvalidDurationError
from athlos.platform.domain.value_object import ValueObject


class Sport(Enum):
    """The three sports this module supports. Each has its own,
    independent aggregate (`RunningActivity`/`CyclingActivity`/
    `GymActivity`) - this enum only labels which one, for the parts of
    the system that need to treat activities uniformly regardless of
    sport (the `ActivityRecorded` event, cross-sport listing).
    """

    RUNNING = "running"
    CYCLING = "cycling"
    GYM = "gym"


@dataclass(frozen=True)
class ActivityId(ValueObject):
    """Identity shared by the three activity aggregates - not a shared
    aggregate, just a shared identity *type*, so cross-sport listing can
    reference "an activity id" without knowing which sport it belongs
    to. Server-generated, like `UserId`.
    """

    value: uuid.UUID

    @classmethod
    def generate(cls) -> "ActivityId":
        return cls(uuid.uuid4())


@dataclass(frozen=True)
class Duration(ValueObject):
    """A duration in whole seconds. Must be strictly positive - a
    recorded activity that took zero time is not a valid recording.
    """

    seconds: int

    def __post_init__(self) -> None:
        if self.seconds <= 0:
            raise InvalidDurationError(self.seconds)


@dataclass(frozen=True)
class Distance(ValueObject):
    """A distance in meters. Must be strictly positive, same reasoning
    as `Duration`.
    """

    meters: float

    def __post_init__(self) -> None:
        if self.meters <= 0:
            raise InvalidDistanceError(self.meters)
