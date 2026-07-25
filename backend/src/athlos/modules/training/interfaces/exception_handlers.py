"""Translation of training's domain exceptions into HTTP responses.

Lives here, not in `api/`, so the shared composition layer never has to
import training's domain exceptions - same reasoning as `identity`
(see docs/DECISIONS.md).
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from athlos.modules.training.domain.exceptions import (
    ActivityNotFoundError,
    InvalidDistanceError,
    InvalidDurationError,
)


def register(app: FastAPI) -> None:
    @app.exception_handler(InvalidDurationError)
    def _handle_invalid_duration(_request: Request, exc: InvalidDurationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidDistanceError)
    def _handle_invalid_distance(_request: Request, exc: InvalidDistanceError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ActivityNotFoundError)
    def _handle_activity_not_found(_request: Request, exc: ActivityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
