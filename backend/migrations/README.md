# Migrations

Alembic esta configurado (`../alembic.ini`, `env.py`, `script.py.mako`),
pero `target_metadata` en `env.py` es `None`: todavia no existe ningun
modelo de dominio al que generar migraciones. No hay ninguna revision en
este directorio. Cuando exista la `Base` declarativa del shared kernel
(Fase 2 del roadmap), `env.py` se actualizara para apuntar a ella y podran
generarse migraciones reales con `alembic revision --autogenerate`.
