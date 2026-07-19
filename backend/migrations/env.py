"""Alembic environment.

`target_metadata` apunta a la `Base` declarativa del shared kernel
(`athlos.platform.infrastructure.persistence.database.Base`). Por ahora
esa `Base` solo registra la tabla `outbox_messages` (Fase 2); cada modulo
de negocio futuro extendera la misma `Base`, y `--autogenerate` los vera
automaticamente sin tener que volver a tocar este archivo. Todavia no se
ha generado ninguna migracion real: eso se hara cuando exista tambien un
Postgres real contra el que generarla (Fase 3 en adelante).
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Importa los modulos ORM del shared kernel para que sus tablas queden
# registradas en `Base.metadata` antes de que Alembic la use.
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
