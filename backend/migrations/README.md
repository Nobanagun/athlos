# Migrations

Alembic esta configurado (`../alembic.ini`, `env.py`, `script.py.mako`).
`target_metadata` en `env.py` ya apunta a la `Base` declarativa del shared
kernel (`athlos.platform.infrastructure.persistence.database.Base`), que
por ahora solo registra la tabla `outbox_messages` (Fase 2). Todavia no
hay ninguna revision en este directorio: generar la primera migracion real
con `alembic revision --autogenerate` requiere un Postgres real contra el
que ejecutarla, y se hara junto con el primer modelo de dominio de negocio
(Fase 3 en adelante).
