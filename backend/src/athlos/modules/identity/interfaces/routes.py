"""HTTP routes for the identity module."""

from fastapi import APIRouter, Depends, status

from athlos.modules.identity.application.login_user import LoginUserCommand, LoginUserHandler
from athlos.modules.identity.application.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from athlos.modules.identity.domain.user import User
from athlos.modules.identity.interfaces.dependencies import (
    get_current_user,
    get_login_user_handler,
    get_register_user_handler,
)
from athlos.modules.identity.interfaces.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    UserResponse,
)

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
