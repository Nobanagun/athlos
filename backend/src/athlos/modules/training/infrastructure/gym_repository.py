"""SQLAlchemy-backed implementation of the gym activity repository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.modules.training.application.ports import GymActivityRepository
from athlos.modules.training.domain.gym.activity import GymActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.modules.training.infrastructure.models import _MappedGymActivity
from athlos.platform.domain.user_id import UserId


class SqlAlchemyGymActivityRepository(GymActivityRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, activity: GymActivity) -> None:
        self._session.add(_MappedGymActivity.from_domain(activity))

    def get_by_user(self, user_id: UserId) -> list[GymActivity]:
        stmt = select(_MappedGymActivity).where(_MappedGymActivity.user_id == user_id)
        return list(self._session.scalars(stmt).all())

    def get_by_user_and_id(self, user_id: UserId, activity_id: ActivityId) -> GymActivity | None:
        stmt = select(_MappedGymActivity).where(
            _MappedGymActivity.user_id == user_id, _MappedGymActivity.id == activity_id
        )
        return self._session.scalars(stmt).first()
