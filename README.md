# Athlos

Plataforma multiplataforma de entrenamiento deportivo que combina
funciones de Garmin Connect, TrainingPeaks, Strava, Hevy y Whoop:
running, ciclismo, gimnasio, recuperación, planificación, estadísticas y
un entrenador basado en IA.

> **Estado actual: fase de estructura inicial.** Este repositorio contiene
> únicamente el andamiaje (carpetas, manifiestos y documentación) del
> proyecto. No hay dependencias instaladas, no hay lógica de negocio
> implementada y no se ha realizado ningún commit todavía.

## Arquitectura

- **Backend**: monolito modular en Python (FastAPI), organizado por
  bounded contexts siguiendo Domain-Driven Design, con Repository
  Pattern, Unit of Work, eventos de dominio y Transactional Outbox.
  Ver [`backend/README.md`](backend/README.md).
- **Frontend móvil** (principal): React Native + Expo + TypeScript, con
  Expo Router, diseñado offline-first. Ver
  [`frontend/mobile/README.md`](frontend/mobile/README.md).
- **Frontend web** (planificado, no implementado): Next.js + TypeScript
  para dashboard y administración. Ver
  [`frontend/web/README.md`](frontend/web/README.md).
- La arquitectura completa está documentada en
  [`docs/architecture/overview.md`](docs/architecture/overview.md).

## Estructura del repositorio

```
athlos/
├── backend/     # API y lógica de negocio (monolito modular, DDD)
├── frontend/
│   ├── mobile/   # App React Native + Expo (principal)
│   └── web/      # Dashboard Next.js (planificado)
├── docs/        # Documentación de arquitectura y ADRs
├── infra/       # Docker y configuración de infraestructura local
├── tests/       # Tests de integración y e2e (cross-servicio)
└── scripts/     # Scripts de soporte para desarrollo
```

## Primeros pasos

Todavía no hay nada que instalar ni ejecutar: esta fase solo define la
estructura. Los siguientes pasos (elegir versiones de dependencias,
bootstrap real de FastAPI y Expo, primera migración de base de datos)
se abordarán en una fase posterior.

## Documentación

- [`docs/architecture/overview.md`](docs/architecture/overview.md) - visión
  general de la arquitectura.
- [`docs/architecture/ddd.md`](docs/architecture/ddd.md) - patrones DDD.
- [`docs/architecture/offline-sync.md`](docs/architecture/offline-sync.md) -
  estrategia offline-first (borrador).
- [`docs/adr/`](docs/adr/) - Architecture Decision Records.
