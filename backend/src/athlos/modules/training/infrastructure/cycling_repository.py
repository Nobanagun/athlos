"""SQLAlchemy-backed implementation of the cycling activity repository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.modules.training.application.ports import CyclingActivityRepository
from athlos.modules.training.domain.cycling.activity import CyclingActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.modules.training.infrastructure.models import _MappedCyclingActivity
from athlos.platform.domain.user_id import UserId


class SqlAlchemyCyclingActivityRepository(CyclingActivityRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, activity: CyclingActivity) -> None:
        self._session.add(_MappedCyclingActivity.from_domain(activity))

    def get_by_user(self, user_id: UserId) -> list[CyclingActivity]:
        stmt = select(_MappedCyclingActivity).where(_MappedCyclingActivity.user_id == user_id)
        return list(self._session.scalars(stmt).all())

    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> CyclingActivity | None:
        stmt = select(_MappedCyclingActivity).where(
            _MappedCyclingActivity.user_id == user_id, _MappedCyclingActivity.id == activity_id
        )
        return self._session.scalars(stmt).first()
