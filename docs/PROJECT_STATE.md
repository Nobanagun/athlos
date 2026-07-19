# Project State

> Última actualización: 2026-07-19
> Este documento es la fuente de verdad sobre el estado real del proyecto.
> Debe actualizarse cada vez que cambie algo significativo (stack, estructura,
> fase actual). Si este documento contradice el código, el código manda —
> pero la contradicción debe corregirse aquí de inmediato.

## Estado actual

Fase 1 en curso — **bootstrap del backend completado** (PR #1,
`feature/bootstrap-backend`). El backend tiene ahora un entorno de
desarrollo real: dependencias instaladas y fijadas con `uv`, linting
(Ruff), type checking estricto (mypy) y tests (pytest) configurados y en
verde, y hooks de `pre-commit` funcionando. **Sigue sin haber ninguna
funcionalidad de negocio implementada**: ni modelos de dominio con
lógica, ni endpoints de negocio (solo un `GET /health` de verificación),
ni migraciones reales, ni pantallas de la app móvil.

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
  uno con capas `domain/application/infrastructure/interfaces`.
- Todos los archivos `.py` de `modules/` y `platform/` siguen siendo
  **placeholders con docstring**, sin imports ni lógica — el bootstrap no
  ha tocado el dominio.
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
  `script.py.mako`) pero `target_metadata = None` — sin ninguna migración
  real todavía, a la espera del shared kernel (Fase 2).
- Sin base de datos ni Redis en ejecución — los drivers están instalados
  pero no hay ningún servicio real levantado (eso es Fase 1, sección de
  infraestructura Docker, todavía pendiente).

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

Bootstrap del backend completado; queda pendiente el resto de la Fase 1
(CI en `.github/workflows/`, servicios reales en
`infra/docker/docker-compose.yml`, bootstrap real de la app móvil con
Expo) y, en paralelo o a continuación, la Fase 2: construcción del shared
kernel (`platform/`: Entity, AggregateRoot, Value Object, Unit of Work,
Transactional Outbox) como base para implementar el primer módulo de
negocio de extremo a extremo. Ver Fase 1 y Fase 2 en
[`ROADMAP.md`](ROADMAP.md).
