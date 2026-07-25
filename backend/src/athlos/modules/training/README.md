# Training

Primer módulo de negocio del proyecto (Fase 4) — running, ciclismo y
gimnasio/fuerza. Implementado end-to-end (dominio, aplicación,
persistencia, API) y sirve de **plantilla de referencia** para el resto
de bounded contexts de negocio (`recovery`/`planning` en Fase 6,
`analytics`/`coaching` en Fase 7): mismo reparto de capas, mismos
patrones (`_MappedX` + `TypeDecorator`, un handler por caso de uso,
excepciones anti-enumeración) que ya se establecieron en `identity`.

Ver `docs/DECISIONS.md` (entradas de Fase 4) para el detalle completo
de cada decisión y las alternativas descartadas.

## Modelo de dominio

Cada deporte es un **agregado completamente independiente** —
`RunningActivity`, `CyclingActivity`, `GymActivity` (en
`domain/{running,cycling,gym}/`) — sin base de clase común ni herencia
entre ellos, cada uno con su propia tabla y repositorio. Lo único
compartido, en la raíz de `domain/`:

- `ActivityId` — identidad de los tres agregados (no `platform/`:
  ningún otro módulo lo necesita todavía).
- `Duration`/`Distance` — value objects en unidades SI (segundos,
  metros), ambos estrictamente positivos. La conversión a otras
  unidades (millas, pies) es responsabilidad exclusiva del cliente.
- `ActivitySummary` — un `Protocol` mínimo (`id`/`user_id`/`sport`/
  `started_at`), el único contrato estructural entre los tres deportes,
  usado para listarlos juntos sin acoplarlos entre sí.
- `ActivityRecorded` — evento de dominio genérico (sin métricas
  específicas del deporte en el payload), publicado vía el
  Transactional Outbox del shared kernel.

`GymActivity` es deliberadamente mínimo en este incremento: solo
duración y fecha de inicio, sin desglose de ejercicios (series,
repeticiones, peso) — ver `DECISIONS.md` para el razonamiento.

## Aplicación

Un handler y un repositorio por deporte (`RegisterXActivityHandler`,
`GetXActivityHandler`, `XActivityRepository`) — sin caso de uso
unificado con una rama `if/elif` interna. La única excepción cross-sport
es `ListUserActivitiesHandler`, que orquesta los tres repositorios y
fusiona el resultado en Python (sin modelo de lectura/proyección
dedicado, no justificado todavía por el volumen de datos).

## API

```
POST   /activities/running
POST   /activities/cycling
POST   /activities/gym
GET    /activities                       # listado cross-sport (DTO mínimo)
GET    /activities/running/{id}
GET    /activities/cycling/{id}
GET    /activities/gym/{id}
```

Todos protegidos con el JWT ya emitido por `identity` (mismo mecanismo,
sin reimplementar autenticación). `GET /activities/{sport}/{id}`
devuelve `404` genérico tanto si la actividad no existe como si
pertenece a otro usuario (mismo criterio anti-enumeración que
`DeviceNotFoundError` en `identity`).

## Cliente móvil

Solo lectura en este incremento (`frontend/mobile/src/data/remote/training.ts`,
`src/domain/training.ts`, pantallas en `app/(app)/activities/`) — sin
formulario de registro de actividades todavía, aunque el backend ya lo
soporta. Ver `docs/DECISIONS.md` (incremento 6) para el detalle.

## Estado y pendientes

Backend y cliente móvil verificados con tests automatizados (152 +
16). **Sin validar todavía en un simulador o dispositivo real** — la
única verificación manual pendiente antes de dar la Fase 4 por
cerrada. Persistencia local offline y sincronización quedan fuera de
alcance de este módulo (Fase 5, módulo `sync`).
