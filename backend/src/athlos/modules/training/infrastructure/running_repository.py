"""SQLAlchemy-backed implementation of the running activity repository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.modules.training.application.ports import RunningActivityRepository
from athlos.modules.training.domain.running.activity import RunningActivity
from athlos.modules.training.domain.value_objects import ActivityId
from athlos.modules.training.infrastructure.models import _MappedRunningActivity
from athlos.platform.domain.user_id import UserId


class SqlAlchemyRunningActivityRepository(RunningActivityRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, activity: RunningActivity) -> None:
        self._session.add(_MappedRunningActivity.from_domain(activity))

    def get_by_user(self, user_id: UserId) -> list[RunningActivity]:
        stmt = select(_MappedRunningActivity).where(_MappedRunningActivity.user_id == user_id)
        return list(self._session.scalars(stmt).all())

    def get_by_user_and_id(
        self, user_id: UserId, activity_id: ActivityId
    ) -> RunningActivity | None:
        stmt = select(_MappedRunningActivity).where(
            _MappedRunningActivity.user_id == user_id, _MappedRunningActivity.id == activity_id
        )
        return self._session.scalars(stmt).first()
