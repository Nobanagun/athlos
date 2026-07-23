# Migrations

Alembic esta configurado (`../alembic.ini`, `env.py`, `script.py.mako`).
`target_metadata` en `env.py` apunta a la `Base` declarativa del shared
kernel (`athlos.platform.infrastructure.persistence.database.Base`), que
registra `outbox_messages` (Fase 2) y `users` (Fase 3, `identity`).
Todavia no hay ninguna revision en este directorio: generar la primera
migracion real con `alembic revision --autogenerate` requiere un
Postgres real contra el que ejecutarla.

## Registro manual obligatorio por modulo

Que un modelo ORM extienda `Base` **no** es suficiente para que Alembic
lo vea. Su clase declarativa tiene que ejecutarse (importarse) antes de
que `create_all()`/`--autogenerate` inspeccionen `Base.metadata`. Como
todavia no existe un mecanismo de descubrimiento automatico de modulos,
`migrations/env.py` importa explicitamente el modulo de modelos de cada
bounded context con infraestructura propia:

```python
from athlos.platform.infrastructure.outbox import models as _outbox_models  # noqa: F401
from athlos.modules.identity.infrastructure import models as _identity_models  # noqa: F401
```

**Al anadir infraestructura de persistencia a un modulo nuevo, hay que
anadir aqui su propio import** — olvidarlo deja esa tabla invisible para
Alembic sin ningun error visible en el momento. Ver la entrada
correspondiente en `docs/DECISIONS.md` para el contexto completo de esta
limitacion.
