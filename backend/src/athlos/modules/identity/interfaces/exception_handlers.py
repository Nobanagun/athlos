"""Translation of identity's domain exceptions into HTTP responses.

Lives here, not in `api/`, so that the shared composition layer never
has to import identity's domain exceptions - each module owns the
translation of its own errors (see docs/DECISIONS.md).

Deliberately does not translate `sqlalchemy.exc.IntegrityError` (a
race-condition duplicate that slips past `EmailAlreadyRegisteredError`'s
application-level check): out of scope for this increment, propagates
as a 500. See docs/DECISIONS.md for the justification.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from athlos.modules.identity.domain.exceptions import (
    DeviceNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidTokenError,
    WeakPasswordError,
)


def register(app: FastAPI) -> None:
    @app.exception_handler(InvalidEmailError)
    def _handle_invalid_email(_request: Request, exc: InvalidEmailError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(EmailAlreadyRegisteredError)
    def _handle_email_already_registered(
        _request: Request, exc: EmailAlreadyRegisteredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(WeakPasswordError)
    def _handle_weak_password(_request: Request, exc: WeakPasswordError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidCredentialsError)
    def _handle_invalid_credentials(
        _request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidTokenError)
    def _handle_invalid_token(_request: Request, exc: InvalidTokenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(DeviceNotFoundError)
    def _handle_device_not_found(_request: Request, exc: DeviceNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
