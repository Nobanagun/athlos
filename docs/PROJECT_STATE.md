# Project State

> Última actualización: 2026-07-24
> Este documento es la fuente de verdad sobre el estado real del proyecto.
> Debe actualizarse cada vez que cambie algo significativo (stack, estructura,
> fase actual). Si este documento contradice el código, el código manda —
> pero la contradicción debe corregirse aquí de inmediato.

## Estado actual

Fase 1 (bootstrap del backend, PR #1), Fase 2 (shared kernel de
`platform/`, PR #2) y **Fase 3 (`identity`, PR #3-#6) completadas**.
Cinco incrementos: (1) dominio + aplicación (`User`, `UserId`,
`Email`, `AccountStatus` solo `ACTIVE`, `UserRegistered`,
`UserRepository`, `RegisterUserHandler`); (2) infraestructura de
persistencia real (`SqlAlchemyUserRepository`, mapeo declarativo de
`User` vía subclase + `TypeDecorator` para `UserId`/`Email`, restricción
`UNIQUE` de email real); (3) `identity/interfaces` — primer endpoint HTTP
real del proyecto, `POST /users`; (4) **autenticación JWT stateless** —
`User` gana `password_hash` (Argon2id vía `argon2-cffi`), `POST /users`
ahora exige contraseña, `POST /login` emite un JWT (`PyJWT`/HS256, TTL de
1h, sin refresh/rotación/revocación) y `GET /users/me` es el primer
endpoint protegido, resuelto vía la dependencia `get_current_user`; (5)
**dispositivos vinculados** — nuevo agregado `Device` (identidad propia
`DeviceLinkId`, generado por el servidor; `device_id` lo aporta el
cliente, único por `(device_id, user_id)`, no globalmente), `POST
/devices`, `GET /devices` y `DELETE /devices/{device_id}` protegidos con
el mismo JWT, registro idempotente, eventos `DeviceLinked`/
`DeviceUnlinked` vía outbox (el borrado incluido, sin tocar
`platform/`). Con este incremento, los tres criterios de finalización de
la Fase 3 declarados en `ROADMAP.md` quedan cubiertos — alta de usuario,
autenticación básica y registro de dispositivo end-to-end, Repository
Pattern/Unit of Work sobre el shared kernel, tests de integración.
**Revisados y aprobados: la Fase 3 se marca aquí como completada.** El
marcador de fase en `ROADMAP.md` (`⏳` → `✅`) se actualiza como paso
separado, no incluido en esta revisión.

**Corrección puntual en el shared kernel**: se encontró y arregló un bug
real en `AggregateRoot` (`platform/domain/entity.py`) — un agregado
reconstruido por SQLAlchemy desde una fila (no construido en Python)
carecía de `_domain_events` y `.domain_events`/`record_event()`/
`clear_domain_events()` lanzaban `AttributeError`. Ver `DECISIONS.md`
para el análisis completo, la alternativa descartada y la verificación
empírica previa a implementar.

**112 tests en total en el backend, todos en verde.**

Ver [`ROADMAP.md`](ROADMAP.md) para las fases siguientes y
[`docs/agent/OPEN_QUESTIONS.md`](agent/OPEN_QUESTIONS.md) para
limitaciones conocidas (protección de rama pendiente de GitHub Pro).

## Stack tecnológico aprobado

| Área | Tecnología | Estado |
|---|---|---|
| Backend | Python 3.13 + FastAPI 0.139.2 (uv) | Dependencias instaladas y fijadas, sin lógica de negocio |
| Frontend móvil (principal) | React Native + Expo + TypeScript + Expo Router | Elegido, sin bootstrap real todavía |
| Frontend web (dashboard/admin) | Next.js + TypeScript | Elegido, **no implementado**, fase futura |
| Persistencia local (mobile, offline-first) | Por decidir (SQLite / WatermelonDB / Realm) | Pendiente |
| Base de datos backend | Por decidir (candidata: PostgreSQL) | Pendiente |
| Infraestructura local | Docker + Docker Compose | Instalados en la máquina de desarrollo; sin servicios activos aún |
| Control de versiones | Git + GitHub (repo privado) | Configurado |
| CI/CD | GitHub Actions (planeado) | No implementado |
| Licencia | Propietaria, todos los derechos reservados | Aplicada |

## Arquitectura elegida

Monolito modular en el backend, organizado por bounded contexts siguiendo
Domain-Driven Design, con Repository Pattern, Unit of Work, eventos de
dominio y Transactional Outbox. Cliente móvil offline-first con
sincronización multi-dispositivo. El entrenador de IA (`coaching`) está
arquitectónicamente separado de la lógica determinista del resto de
módulos. Detalle completo en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Estructura del repositorio

```
athlos/
├── backend/                # Monolito modular Python/FastAPI (DDD)
│   └── src/athlos/
│       ├── modules/         # 8 bounded contexts (ver ARCHITECTURE.md)
│       ├── platform/         # Shared kernel (UoW, outbox, domain base)
│       ├── api/               # Composición de la app (FastAPI)
│       └── config/             # Settings (placeholder)
├── frontend/
│   ├── mobile/              # React Native + Expo (app principal)
│   └── web/                 # Next.js (reservado, no implementado)
├── docs/                    # Este documento y el resto de la documentación
├── infra/                   # Docker (placeholder, sin servicios activos)
├── tests/                   # Tests de integración/e2e cross-servicio
├── scripts/                 # Scripts de soporte (placeholder)
├── .github/CODEOWNERS       # @Nobanagun propietario de todo el repo
└── LICENSE                  # Propietaria
```

## Estado por área

### Backend

- Estructura de carpetas de los 8 módulos (bounded contexts) creada, cada
  uno con capas `domain/application/infrastructure/interfaces`. **7 de 8
  módulos siguen siendo placeholders con docstring** (`training`,
  `recovery`, `planning`, `coaching`, `analytics`, `sync`,
  `integrations`).
- **`identity` (Fase 3, incrementos 1-5)**: `domain/` gana `PasswordHash`
  (value object, sin validación propia), `User` con `password_hash`,
  `WeakPasswordError`/`InvalidCredentialsError`/`InvalidTokenError`
  (incremento 4, además de `InvalidEmailError` del incremento 3), y el
  agregado `Device` (incremento 5, identidad `DeviceLinkId` generada por
  el servidor, campos `device_id`/`user_id`/`registered_at`,
  `DeviceNotFoundError`). `application/` gana los puertos
  `PasswordHasher`/`TokenIssuer`/`DeviceRepository`,
  `RegisterUserHandler` actualizado (hashea y valida fortaleza mínima de
  8 caracteres), `LoginUserHandler` (sin `UnitOfWork` - solo lectura), y
  `RegisterDeviceHandler`/`ListUserDevicesHandler`/`UnlinkDeviceHandler`
  (incremento 5; registro idempotente por `(device_id, user_id)`).
  `infrastructure/` gana `Argon2PasswordHasher` (Argon2id vía
  `argon2-cffi`), `PyJwtTokenIssuer` (HS256, TTL de 1h), la columna
  `password_hash` en `_MappedUser`, y (incremento 5) `_MappedDevice`
  (tabla `devices`, `UNIQUE(device_id, user_id)`) con
  `SqlAlchemyDeviceRepository` y `UtcDateTimeType` (normaliza
  `registered_at` a UTC-naive al guardar y reconstruye `tzinfo=UTC` al
  leer - SQLite descarta el offset de zona horaria incluso con
  `timezone=True`); el resto (`SqlAlchemyUserRepository`, restricción
  `UNIQUE` sobre `users.email`) sin cambios desde el incremento 2.
  **`interfaces/`**: `POST /users` (incremento 3) exige `password`
  desde el incremento 4; `POST /login` y `GET /users/me` (incremento 4);
  `POST /devices`/`GET /devices`/`DELETE /devices/{device_id}`
  (incremento 5, protegidos con el mismo JWT) — `routes.py`,
  `dependencies.py`, `schemas.py` (Pydantic, solo aquí), y
  `exception_handlers.py` (traduce `InvalidEmailError`→422,
  `EmailAlreadyRegisteredError`→409, `WeakPasswordError`→422,
  `InvalidCredentialsError`→401, `InvalidTokenError`→401,
  `DeviceNotFoundError`→404; deja `IntegrityError` de condición de
  carrera sin traducir, propaga como 500 — decisión deliberada, ver
  `DECISIONS.md`).
- **`platform/` (shared kernel) ya tiene implementación real** (Fase 2):
  `Entity`/`AggregateRoot`/`ValueObject`/`DomainEvent` (dominio puro, sin
  SQLAlchemy ni Pydantic); `UnitOfWork`/`EventBus` (contratos);
  `SqlAlchemyUnitOfWork` (concreta, síncrona, con el algoritmo de commit
  documentado en `DECISIONS.md`); `OutboxMessage` + `dispatch_pending()`
  (Transactional Outbox); `InMemoryEventBus`. Sin repositorio genérico
  (no se justificó todavía). Tests en `backend/tests/unit/platform/`.
- Gestor de dependencias: `uv`, con `.python-version` (3.13) y `uv.lock`
  commiteado. `pyproject.toml` declara dependencias reales y fijadas
  (`fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `psycopg`, `redis`,
  `pydantic` en runtime; `pytest`, `httpx2`, `ruff`, `mypy`, `pre-commit`
  en dev — ver `DECISIONS.md` para la justificación de cada versión).
- `backend/src/athlos/api/main.py` es el composition root (sin lógica de
  negocio): expone `GET /health` y ahora también `POST /users` (incluido
  el router de `identity` y su registro de manejadores de excepciones).
  `api/dependencies.py` (nuevo, compartido, agnóstico de negocio):
  `get_session()`/`get_unit_of_work()`, con inicialización perezosa del
  engine (`functools.lru_cache`) para que importar el módulo nunca
  requiera `DATABASE_URL`. `config/settings.py` (nuevo, mínimo): lee
  `DATABASE_URL` de entorno, sin `pydantic-settings`.
- Ruff, mypy (modo `strict`, sin excepciones) y pytest configurados en
  `pyproject.toml` y en verde; `pre-commit` instalado y validado contra
  un `git commit` real.
- Alembic configurado (`alembic.ini`, `migrations/env.py`,
  `script.py.mako`); `target_metadata` apunta a la `Base` del shared
  kernel, que ahora registra `outbox_messages` **y `users`**. Sigue sin
  generarse ninguna migración real — requiere PostgreSQL real, pendiente
  del resto de la Fase 1. **Registro manual obligatorio**: cada módulo
  con infraestructura propia debe añadir su import en `migrations/env.py`
  a mano — no hay descubrimiento automático (ver `DECISIONS.md` y
  `backend/migrations/README.md`).
- Sin base de datos ni Redis en ejecución — los drivers están instalados
  pero no hay ningún servicio real levantado (eso es Fase 1, sección de
  infraestructura Docker, todavía pendiente). Los tests de `platform/` e
  `identity` corren contra SQLite en memoria; **pendiente re-validar
  contra PostgreSQL real** (outbox desde Fase 2, y ahora también la
  restricción `UNIQUE` de `identity`).

### Frontend

- **mobile/**: estructura de carpetas creada (`app/` para Expo Router,
  `src/domain`, `src/data/{local,remote,sync}`, `src/features`,
  `src/shared`). `package.json`/`tsconfig.json`/`app.json` son
  manifiestos sin instalar (`npm install` no ejecutado).
- **web/**: solo existe como carpeta reservada con un README explicando
  que se implementará en una fase posterior.

### Infraestructura

- Docker Desktop y Docker Compose v2 instalados y verificados en la
  máquina de desarrollo.
- `infra/docker/docker-compose.yml` es un placeholder sin servicios
  activos (comentarios de ejemplo para backend/postgres/redis).
- Sin CI configurado (no existe ningún workflow en `.github/workflows/`).
- Repositorio GitHub privado creado (`Nobanagun/athlos`), con `CODEOWNERS`
  aplicado. **Protección de rama pendiente**: GitHub Free no permite
  rulesets/branch protection en repos privados (ver `OPEN_QUESTIONS.md`).

## Próximo objetivo

**Fase 3 (`identity`) completada** — cinco incrementos, 112 tests en
total en el backend, todos en verde. Próximo objetivo: **Fase 4 —
Training**, módulo de referencia que servirá de plantilla para el resto
de bounded contexts de negocio (ver `ROADMAP.md`). Diseño inicial en
preparación, pendiente de revisión antes de implementar nada.

Sin relación de bloqueo con la Fase 4, sigue pendiente: (1) el resto de
la Fase 1 (CI, servicios Docker reales, bootstrap de la app móvil) y,
con Postgres real disponible, generar la primera migración real y
re-validar outbox + restricciones `UNIQUE` (`users.email`,
`devices(device_id, user_id)`) contra él; (2) traducción de
`IntegrityError` por condición de carrera en `identity`, deliberadamente
fuera de alcance hasta ahora (ver `DECISIONS.md`). Ver `ROADMAP.md`.
