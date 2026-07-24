"""FastAPI dependencies specific to the identity module."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from athlos.api.dependencies import get_session, get_unit_of_work
from athlos.config.settings import get_jwt_secret
from athlos.modules.identity.application.list_user_devices import ListUserDevicesHandler
from athlos.modules.identity.application.login_user import LoginUserHandler
from athlos.modules.identity.application.ports import (
    DeviceRepository,
    PasswordHasher,
    TokenIssuer,
    UserRepository,
)
from athlos.modules.identity.application.register_device import RegisterDeviceHandler
from athlos.modules.identity.application.register_user import RegisterUserHandler
from athlos.modules.identity.application.unlink_device import UnlinkDeviceHandler
from athlos.modules.identity.domain.exceptions import InvalidTokenError
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import UserId
from athlos.modules.identity.infrastructure.device_repository import SqlAlchemyDeviceRepository
from athlos.modules.identity.infrastructure.jwt_token_issuer import PyJwtTokenIssuer
from athlos.modules.identity.infrastructure.password_hasher import Argon2PasswordHasher
from athlos.modules.identity.infrastructure.repository import SqlAlchemyUserRepository
from athlos.platform.application.unit_of_work import UnitOfWork

# auto_error=False: a missing Authorization header is handled explicitly
# in get_current_user_id below so it raises the same InvalidTokenError
# (-> 401) as an invalid/expired token, instead of HTTPBearer's own
# default 403.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()


def get_token_issuer() -> TokenIssuer:
    return PyJwtTokenIssuer(get_jwt_secret())


def get_register_user_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    users: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUserHandler:
    return RegisterUserHandler(uow, users, hasher)


def get_login_user_handler(
    users: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
    tokens: TokenIssuer = Depends(get_token_issuer),
) -> LoginUserHandler:
    return LoginUserHandler(users, hasher, tokens)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    tokens: TokenIssuer = Depends(get_token_issuer),
) -> UserId:
    if credentials is None:
        raise InvalidTokenError()
    return tokens.verify(credentials.credentials)


def get_current_user(
    user_id: UserId = Depends(get_current_user_id),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    user = users.get_by_id(user_id)
    if user is None:
        raise InvalidTokenError()
    return user


def get_device_repository(session: Session = Depends(get_session)) -> DeviceRepository:
    return SqlAlchemyDeviceRepository(session)


def get_register_device_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    devices: DeviceRepository = Depends(get_device_repository),
) -> RegisterDeviceHandler:
    return RegisterDeviceHandler(uow, devices)


def get_list_user_devices_handler(
    devices: DeviceRepository = Depends(get_device_repository),
) -> ListUserDevicesHandler:
    return ListUserDevicesHandler(devices)


def get_unlink_device_handler(
    uow: UnitOfWork = Depends(get_unit_of_work),
    devices: DeviceRepository = Depends(get_device_repository),
) -> UnlinkDeviceHandler:
    return UnlinkDeviceHandler(uow, devices)
