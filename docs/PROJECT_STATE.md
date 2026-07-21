# Project State

> Última actualización: 2026-07-21
> Este documento es la fuente de verdad sobre el estado real del proyecto.
> Debe actualizarse cada vez que cambie algo significativo (stack, estructura,
> fase actual). Si este documento contradice el código, el código manda —
> pero la contradicción debe corregirse aquí de inmediato.

## Estado actual

Fase 1 (bootstrap del backend, PR #1) y Fase 2 (shared kernel de
`platform/`, PR #2) completadas. **Fase 3 en curso — primer incremento
del módulo `identity` implementado**: agregado `User`, value objects
`UserId`/`Email`, `AccountStatus` (solo `ACTIVE`), evento
`UserRegistered`, puerto `UserRepository` y el caso de uso
`RegisterUserHandler`. Cubre únicamente identidad de usuario — **sin
autenticación** (sin login, JWT, contraseñas, sesiones ni dispositivos
vinculados) y **sin infraestructura ni HTTP todavía** (sin repositorio
SQLAlchemy real, sin migración, sin endpoints). 14 tests unitarios
nuevos (33 en total en el backend), todos en verde.

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
- **`identity` (Fase 3, incremento 1)**: `domain/` (`User`, `UserId`,
  `Email`, `AccountStatus`, `UserRegistered`,
  `EmailAlreadyRegisteredError`) y `application/` (`UserRepository`
  como puerto específico del módulo, `RegisterUserHandler`)
  implementados y testeados con dobles de prueba (sin base de datos).
  `identity/infrastructure/` e `identity/interfaces/` siguen siendo
  placeholders — deliberadamente diferidos al siguiente incremento (ver
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
- `backend/src/athlos/api/main.py` expone una instancia real de FastAPI
  con un único endpoint `GET /health` (verificación de arranque, no
  negocio).
- Ruff, mypy (modo `strict`, sin excepciones) y pytest configurados en
  `pyproject.toml` y en verde; `pre-commit` instalado y validado contra
  un `git commit` real.
- Alembic configurado (`alembic.ini`, `migrations/env.py`,
  `script.py.mako`); `target_metadata` ya apunta a la `Base` del shared
  kernel (registra `outbox_messages`). Sigue sin generarse ninguna
  migración real — requiere PostgreSQL real, pendiente del resto de la
  Fase 1.
- Sin base de datos ni Redis en ejecución — los drivers están instalados
  pero no hay ningún servicio real levantado (eso es Fase 1, sección de
  infraestructura Docker, todavía pendiente). Los tests del shared kernel
  corren contra SQLite en memoria; **pendiente re-validar el outbox
  contra PostgreSQL real** (ver `DECISIONS.md`).

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

Primer incremento de `identity` (dominio + aplicación) implementado.
Pendiente: (1) el resto de la Fase 1 (CI, servicios Docker reales,
bootstrap de la app móvil) y validar el outbox contra PostgreSQL real;
(2) siguiente incremento de `identity`: `SqlAlchemyUserRepository`,
modelo ORM de `User`, primera migración real, y una restricción `UNIQUE`
de email (ver riesgo pendiente en `DECISIONS.md`). Ver `ROADMAP.md`.
