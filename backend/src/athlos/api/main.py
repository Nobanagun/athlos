"""Application entrypoint.

Composition root: creates the FastAPI app and wires each module's own
router and exception handlers. Contains no business logic itself - just
orchestration. Each module owns and exposes what it needs; this file
only calls it.
"""

from fastapi import FastAPI

from athlos.modules.identity.interfaces import exception_handlers as identity_exception_handlers
from athlos.modules.identity.interfaces.routes import router as identity_router
from athlos.modules.training.interfaces import exception_handlers as training_exception_handlers
from athlos.modules.training.interfaces.routes import router as training_router

app = FastAPI(title="Athlos")

app.include_router(identity_router)
identity_exception_handlers.register(app)

app.include_router(training_router)
training_exception_handlers.register(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
