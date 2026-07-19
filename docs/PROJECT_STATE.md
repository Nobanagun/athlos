# Project State

> Última actualización: 2026-07-19
> Este documento es la fuente de verdad sobre el estado real del proyecto.
> Debe actualizarse cada vez que cambie algo significativo (stack, estructura,
> fase actual). Si este documento contradice el código, el código manda —
> pero la contradicción debe corregirse aquí de inmediato.

## Estado actual

Fase de **estructura y fundamentos**. Existe el andamiaje completo del
monorepo (backend, frontend, docs, infra, tests, scripts), la licencia
propietaria, el repositorio remoto privado en GitHub y la documentación
base de arquitectura y proceso. **No hay ninguna funcionalidad de negocio
implementada todavía**: ni modelos de dominio con lógica, ni endpoints de
API, ni pantallas de la app móvil, ni dependencias instaladas.

Ver [`ROADMAP.md`](ROADMAP.md) para las fases siguientes y
[`docs/agent/OPEN_QUESTIONS.md`](agent/OPEN_QUESTIONS.md) para
limitaciones conocidas (protección de rama pendiente de GitHub Pro).

## Stack tecnológico aprobado

| Área | Tecnología | Estado |
|---|---|---|
| Backend | Python + FastAPI | Elegido, sin dependencias instaladas |
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
- Todos los archivos `.py` son **placeholders con docstring**, sin
  imports ni lógica (no hay dependencias instaladas todavía).
- `pyproject.toml` declara metadata del proyecto pero `dependencies = []`.
- Sin base de datos, sin migraciones, sin ORM configurado.

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

Bootstrap real de dependencias (backend y mobile) y construcción del
shared kernel (`platform/`: Entity, AggregateRoot, Value Object, Unit of
Work, Transactional Outbox) como base para implementar el primer módulo
de negocio de extremo a extremo. Ver Fase 1 y Fase 2 en
[`ROADMAP.md`](ROADMAP.md).
