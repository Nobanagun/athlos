"""SQLAlchemy-backed implementation of the identity repository port."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from athlos.modules.identity.application.ports import UserRepository
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import Email, UserId
from athlos.modules.identity.infrastructure.models import _MappedUser


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(_MappedUser.from_domain(user))

    def get_by_id(self, user_id: UserId) -> User | None:
        return self._session.get(_MappedUser, user_id)

    def get_by_email(self, email: Email) -> User | None:
        stmt = select(_MappedUser).where(_MappedUser.email == email)
        return self._session.scalars(stmt).first()
