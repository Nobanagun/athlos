"""Application entrypoint.

Composition root: creates the FastAPI app and wires each module's own
router and exception handlers. Contains no business logic itself - just
orchestration. Each module owns and exposes what it needs; this file
only calls it.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from athlos.config.settings import get_cors_allowed_origins
from athlos.modules.identity.interfaces import exception_handlers as identity_exception_handlers
from athlos.modules.identity.interfaces.routes import router as identity_router
from athlos.modules.training.interfaces import exception_handlers as training_exception_handlers
from athlos.modules.training.interfaces.routes import router as training_router

app = FastAPI(title="Athlos")

# No middleware at all when no origins are configured (production
# default) - avoids a CORSMiddleware that would just reject everything,
# and keeps "no origins" the same as "no CORS support" rather than a
# middleware silently doing nothing.
allowed_origins = get_cors_allowed_origins()
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(identity_router)
identity_exception_handlers.register(app)

app.include_router(training_router)
training_exception_handlers.register(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
