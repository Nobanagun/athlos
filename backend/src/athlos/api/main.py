"""Application entrypoint.

Compone la app FastAPI. Solo expone verificación de arranque (`/health`);
el registro de routers de cada módulo de negocio llega en fases
posteriores, cuando existan casos de uso reales que exponer.
"""

from fastapi import FastAPI

app = FastAPI(title="Athlos")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
