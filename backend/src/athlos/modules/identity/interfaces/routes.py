"""HTTP routes for the identity module."""

import uuid

from fastapi import APIRouter, Depends, status

from athlos.modules.identity.application.list_user_devices import ListUserDevicesHandler
from athlos.modules.identity.application.login_user import LoginUserCommand, LoginUserHandler
from athlos.modules.identity.application.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceHandler,
)
from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.application.unlink_device import (
    UnlinkDeviceCommand,
    UnlinkDeviceHandler,
)
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.domain.value_objects import DeviceId
from athlos.modules.identity.interfaces.dependencies import (
    get_current_user,
    get_current_user_id,
    get_list_user_devices_handler,
    get_login_user_handler,
    get_register_device_handler,
    get_register_user_handler,
    get_unlink_device_handler,
)
from athlos.modules.identity.interfaces.schemas import (
    DeviceResponse,
    LoginRequest,
    LoginResponse,
    RegisterDeviceRequest,
    RegisterUserRequest,
    RegisterUserResponse,
    UserResponse,
)
from athlos.platform.domain.user_id import UserId

router = APIRouter(tags=["identity"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
def register_user(
    request: RegisterUserRequest,
    handler: RegisterUserHandler = Depends(get_register_user_handler),
) -> RegisterUserResponse:
    user_id = handler.handle(RegisterUserCommand(email=request.email, password=request.password))
    return RegisterUserResponse(id=user_id.value)


@router.post("/login")
def login(
    request: LoginRequest,
    handler: LoginUserHandler = Depends(get_login_user_handler),
) -> LoginResponse:
    token = handler.handle(LoginUserCommand(email=request.email, password=request.password))
    return LoginResponse(access_token=token)


@router.get("/users/me")
def get_current_user_profile(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id.value, email=user.email.value)


@router.post("/devices")
def register_device(
    request: RegisterDeviceRequest,
    user_id: UserId = Depends(get_current_user_id),
    handler: RegisterDeviceHandler = Depends(get_register_device_handler),
) -> DeviceResponse:
    result = handler.handle(
        RegisterDeviceCommand(user_id=user_id, device_id=DeviceId(request.device_id))
    )
    return DeviceResponse(device_id=result.device_id.value, registered_at=result.registered_at)


@router.get("/devices")
def list_devices(
    user_id: UserId = Depends(get_current_user_id),
    handler: ListUserDevicesHandler = Depends(get_list_user_devices_handler),
) -> list[DeviceResponse]:
    devices = handler.handle(user_id)
    return [
        DeviceResponse(device_id=device.device_id.value, registered_at=device.registered_at)
        for device in devices
    ]


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_device(
    device_id: uuid.UUID,
    user_id: UserId = Depends(get_current_user_id),
    handler: UnlinkDeviceHandler = Depends(get_unlink_device_handler),
) -> None:
    handler.handle(UnlinkDeviceCommand(user_id=user_id, device_id=DeviceId(device_id)))
