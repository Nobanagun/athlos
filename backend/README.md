# Athlos Backend

Monolito modular en Python organizado por bounded contexts (Domain-Driven
Design). Cada modulo encapsula sus propias capas de dominio, aplicacion,
infraestructura e interfaces, comunicandose con el resto del sistema a
traves de eventos de dominio publicados de forma fiable mediante el patron
Transactional Outbox.

> Estado actual: shared kernel (`platform/`) y el modulo `identity`
> (dominio, aplicacion, infraestructura de persistencia e interfaz HTTP -
> `POST /users`) implementados y testeados. El resto de modulos
> (`training`, `recovery`, `planning`, `coaching`, `analytics`, `sync`,
> `integrations`) siguen siendo solo estructura de carpetas y docstrings.
> Ver `docs/PROJECT_STATE.md` para el detalle exacto y actualizado.

## Patrones arquitectonicos

- **Repository Pattern** - abstrae el acceso a datos detras de interfaces
  de dominio.
- **Unit of Work** - agrupa cambios en varios repositorios dentro de una
  misma transaccion.
- **Domain Events** - comunican cambios relevantes entre modulos sin
  acoplarlos directamente.
- **Transactional Outbox** - garantiza la publicacion fiable de eventos de
  dominio junto con el cambio de estado que los origina.

## Modulos (bounded contexts)

| Modulo | Responsabilidad |
|---|---|
| `identity` | Usuarios, autenticacion, perfiles y dispositivos vinculados |
| `training` | Actividades de running, ciclismo y gimnasio |
| `recovery` | Sueno, HRV, fatiga y readiness |
| `planning` | Planes de entrenamiento, periodizacion y calendario |
| `coaching` | Entrenador basado en IA y recomendaciones adaptativas |
| `analytics` | Estadisticas agregadas y metricas de rendimiento |
| `sync` | Sincronizacion offline-first multi-dispositivo |
| `integrations` | Adaptadores para Garmin, Strava, Whoop, TrainingPeaks, Hevy |

`platform/` contiene el shared kernel: building blocks de dominio y los
contratos/infraestructura compartidos (Unit of Work, bus de eventos,
outbox).

## Estructura

```
backend/
├── src/athlos/
│   ├── api/            # Composition root (FastAPI) + dependencias compartidas
│   ├── config/          # Settings minimos (DATABASE_URL)
│   ├── modules/          # Bounded contexts (ver tabla arriba)
│   └── platform/         # Shared kernel
├── tests/                # Tests unitarios e integracion del backend
└── migrations/           # Migraciones de base de datos (pendiente)
```

## Siguiente fase (no incluida todavia)

- Servicios Docker reales (Postgres) y CI (resto de la Fase 1 pendiente).
- Primera migracion real de Alembic contra Postgres.
- Traduccion de `IntegrityError` por condicion de carrera en `identity`
  (deliberadamente fuera del incremento 3 - ver `docs/DECISIONS.md`).
- Autenticacion y dispositivos vinculados en `identity` (Fase 3), o
  avanzar a `training` (Fase 4) usando `identity` como modulo de
  referencia ya persistente y accesible por HTTP.
