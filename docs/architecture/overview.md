# Vision general de la arquitectura

Athlos es una plataforma multiplataforma de entrenamiento deportivo que
combina funciones de Garmin Connect, TrainingPeaks, Strava, Hevy y Whoop:
running, ciclismo, gimnasio, recuperacion, planificacion, estadisticas y
un entrenador basado en IA.

## Backend

Monolito modular en Python (FastAPI), organizado por bounded contexts
(DDD). Ver [ddd.md](ddd.md) para los patrones usados y `backend/README.md`
para el detalle de modulos.

## Frontend

- **mobile** (principal): React Native + Expo + TypeScript, Expo Router,
  offline-first. Cliente principal para iOS y Android.
- **web** (planificado): Next.js + TypeScript, dashboard de administracion
  y visualizacion avanzada. No implementado todavia.

## Principios

- Modularidad por dominio: cada bounded context es independiente y se
  comunica con el resto mediante eventos de dominio.
- Offline-first: la app movil debe ser utilizable sin conexion.
- Sincronizacion multi-dispositivo: ver [offline-sync.md](offline-sync.md).

## Bounded contexts

`identity`, `training` (running/ciclismo/gimnasio), `recovery`,
`planning`, `coaching`, `analytics`, `sync`, `integrations` (Garmin,
Strava, Whoop, TrainingPeaks, Hevy).

> Estado: fase de estructura inicial. Ningun modulo tiene logica de
> negocio implementada todavia.
