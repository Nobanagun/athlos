"""Alembic environment.

`target_metadata` apunta a la `Base` declarativa del shared kernel
(`athlos.platform.infrastructure.persistence.database.Base`), que ahora
registra `outbox_messages` (Fase 2) y `users` (Fase 3). Todavia no se ha
generado ninguna migracion real: eso se hara cuando exista tambien un
Postgres real contra el que generarla.

IMPORTANTE: extender `Base` en un modulo nuevo NO basta para que
Alembic lo vea. Mientras no exista un mecanismo de descubrimiento
automatico, cada modulo con infraestructura de persistencia propia debe
anadir aqui, a mano, un import de su modulo de modelos ORM (como se hace
abajo) para que su clase declarativa se ejecute y quede registrada en
`Base.metadata` antes del `create_all()`/autogenerate. Ver
`docs/DECISIONS.md` (entrada de infraestructura de `identity`, Fase 3) y
`backend/migrations/README.md`.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Importa los modulos ORM de cada modulo/shared kernel para que sus
# tablas queden registradas en `Base.metadata` antes de que Alembic la
# use. Registro manual obligatorio por modulo (ver docstring arriba).
from athlos.modules.identity.infrastructure import models as _identity_models  # noqa: F401
from athlos.platform.infrastructure.outbox import models as _outbox_models  # noqa: F401
from athlos.platform.infrastructure.persistence.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
