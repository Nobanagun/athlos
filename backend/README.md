# Athlos Backend

Monolito modular en Python organizado por bounded contexts (Domain-Driven
Design). Cada modulo encapsula sus propias capas de dominio, aplicacion,
infraestructura e interfaces, comunicandose con el resto del sistema a
traves de eventos de dominio publicados de forma fiable mediante el patron
Transactional Outbox.

> Estado actual: solo existe la estructura de carpetas y los contratos
> conceptuales (docstrings). No hay dependencias instaladas ni logica de
> negocio implementada todavia.

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
│   ├── api/            # Composicion de la app (FastAPI) - punto de entrada
│   ├── config/          # Settings y configuracion (placeholder)
│   ├── modules/          # Bounded contexts (ver tabla arriba)
│   └── platform/         # Shared kernel
├── tests/                # Tests unitarios e integracion del backend
└── migrations/           # Migraciones de base de datos (pendiente)
```

## Siguiente fase (no incluida todavia)

- Elegir e instalar dependencias (FastAPI, SQLAlchemy, etc.).
- Definir el modelo de persistencia y generar la primera migracion.
- Implementar el primer modulo end-to-end como referencia.
