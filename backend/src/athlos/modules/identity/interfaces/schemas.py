"""Pydantic request/response models for the identity HTTP interface.

DTOs live only here - `identity/domain` and `identity/application` never
import Pydantic.
"""

import uuid

from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    email: str
    password: str


class RegisterUserResponse(BaseModel):
    id: uuid.UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
