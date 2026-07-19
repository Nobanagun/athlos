# Architecture

Este documento explica la arquitectura completa de Athlos: por qué se
eligió cada patrón y cómo encajan entre sí. Para el listado de bounded
contexts y su responsabilidad puntual, ver `backend/README.md` y
`docs/architecture/overview.md`. Para el detalle de cada patrón DDD, ver
también `docs/architecture/ddd.md` (este documento es el más completo y
los anteriores quedan como resúmenes de referencia rápida).

## Visión general

Athlos combina funciones de Garmin Connect, TrainingPeaks, Strava, Hevy y
Whoop: running, ciclismo, gimnasio, recuperación, planificación,
estadísticas y un entrenador basado en IA. Dos restricciones de arquitectura
son innegociables desde el diseño inicial:

1. **Offline-first**: la app móvil debe ser completamente usable sin
   conexión.
2. **Sincronización multi-dispositivo**: los datos de un usuario deben
   converger entre todos sus dispositivos.

Todo lo demás (elección de patrones DDD, separación de la IA, event-driven
entre módulos) existe para sostener esas dos restricciones sin que el
sistema se vuelva inmanejable a medida que crecen los bounded contexts.

## Modular Monolith

El backend es **un único desplegable**, no microservicios, pero
internamente está particionado en módulos con fronteras estrictas
(bounded contexts). Se eligió monolito modular en vez de microservicios
por:

- Un solo desarrollador en esta fase: el coste operativo de
  microservicios (orquestación, observabilidad distribuida, versionado de
  contratos entre servicios) no se justifica todavía.
- Las fronteras de módulo se pueden diseñar con la misma disciplina que en
  microservicios (comunicación solo vía eventos de dominio o interfaces de
  aplicación explícitas) y extraerse a servicios independientes más
  adelante si el crecimiento del equipo o la carga lo justifican.

**Regla de frontera**: ningún módulo accede directamente al repositorio o
las tablas de otro módulo. Toda comunicación cruzada pasa por:
- Eventos de dominio (para reacciones asíncronas, desacopladas), o
- Interfaces de aplicación explícitamente expuestas (para consultas
  síncronas necesarias, minimizadas todo lo posible).

## Domain-Driven Design (DDD)

Cada módulo de `backend/src/athlos/modules/` es un bounded context con sus
propias capas:

- **`domain/`** — entidades, agregados, value objects y eventos de
  dominio. Sin dependencias de frameworks ni de infraestructura.
- **`application/`** — casos de uso / servicios de aplicación. Orquestan
  el dominio y dependen de *interfaces* de repositorio, no de
  implementaciones concretas.
- **`infrastructure/`** — implementaciones concretas de esas interfaces
  (persistencia, adaptadores externos).
- **`interfaces/`** — la capa expuesta hacia fuera (routers de FastAPI),
  que traduce HTTP ↔ casos de uso.

Los bounded contexts identificados: `identity`, `training` (con
subdominios `running`/`cycling`/`gym`), `recovery`, `planning`,
`coaching`, `analytics`, `sync`, `integrations`. El detalle de
responsabilidad de cada uno está en `backend/README.md`.

`platform/` es el **shared kernel**: los building blocks de dominio
(`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`) y los contratos
de aplicación compartidos (Unit of Work, bus de eventos) que todo módulo
puede depender sin romper el aislamiento entre bounded contexts —
depender del shared kernel no es depender de otro módulo de negocio.

## Repository Pattern

Cada módulo define sus repositorios como **interfaces en la capa de
dominio o aplicación** (p. ej. `ActivityRepository` en `training`), nunca
como clases concretas de SQLAlchemy expuestas directamente al dominio. La
implementación concreta vive en `infrastructure/`. Esto permite:

- Testear la lógica de dominio y aplicación sin base de datos real (dobles
  de prueba que implementan la misma interfaz).
- Cambiar el motor de persistencia sin tocar el dominio.

## Unit of Work

El patrón Unit of Work coordina cambios sobre uno o varios repositorios
dentro de una única transacción. Es lo que permite que, en el mismo commit
de base de datos, se guarde el cambio de estado de un agregado **y** el
evento de dominio correspondiente en la tabla de outbox (ver siguiente
sección). La interfaz vive en `platform/application`; cada módulo la usa,
no la reimplementa.

## Transactional Outbox

Problema que resuelve: si un módulo escribe en su tabla de negocio y
**después** intenta publicar un evento a un bus de mensajería como dos
pasos separados, un fallo entre medias deja el sistema inconsistente
(el llamado *dual write problem*).

Solución: el evento de dominio se escribe en una tabla `outbox` **dentro
de la misma transacción** que el cambio de estado (vía la misma Unit of
Work). Un proceso de despacho independiente lee la tabla `outbox`,
publica los eventos pendientes al bus de eventos, y los marca como
enviados. Esto garantiza *at-least-once delivery* sin acoplar la
consistencia de los datos a la disponibilidad del bus de mensajería.

Implementación reservada en `platform/infrastructure/outbox`.

## Event-Driven (comunicación entre módulos)

Los módulos no se llaman entre sí de forma síncrona salvo necesidad
explícita. En su lugar, publican **eventos de dominio** (vía el
Transactional Outbox) a los que otros módulos pueden suscribirse. Ejemplos
de flujo previsto:

- `training` publica `ActivityRecorded` → `recovery` y `analytics`
  reaccionan actualizando sus propias proyecciones, sin que `training`
  necesite conocer su existencia.
- `planning` reacciona a eventos de `recovery` (p. ej. bajo readiness) para
  sugerir ajustes de calendario.

Esto mantiene los módulos débilmente acoplados y permite que, si en el
futuro se extraen a servicios independientes, la forma de comunicarse
apenas cambie (el bus de eventos interno se sustituye por uno externo,
pero el contrato de eventos se mantiene).

## Offline-First

La app móvil (`frontend/mobile`) trata la conexión a red como un caso
opcional, no como requisito:

- Toda escritura del usuario se persiste primero localmente
  (`src/data/local`).
- Las pantallas leen del almacenamiento local, nunca directamente de la
  red, para que la UI responda igual con o sin conexión.
- Los cambios pendientes de sincronizar se encolan en `src/data/sync` y se
  envían al backend cuando hay conectividad.

## Sincronización entre dispositivos

El módulo `sync` (backend) y `src/data/sync` (mobile) son contrapartes del
mismo problema: un usuario con varios dispositivos debe ver un estado
convergente. Responsabilidades:

- Backend (`modules/sync`): recibe lotes de cambios de cada dispositivo,
  determina el orden causal, resuelve o marca conflictos, y distribuye los
  cambios resultantes al resto de dispositivos del usuario.
- Mobile (`data/sync`): mantiene la cola local de cambios no confirmados,
  reintenta el envío, y aplica los cambios recibidos de otros
  dispositivos sobre el almacenamiento local.

La estrategia concreta de resolución de conflictos (last-write-wins vs.
CRDTs vs. vector clocks) todavía **no está decidida** — es un borrador
abierto en `docs/architecture/offline-sync.md` y debe cerrarse antes de
implementar la Fase 5 del `ROADMAP.md`.

## IA separada de la lógica determinista

El módulo `coaching` (entrenador basado en IA) está deliberadamente
aislado del resto de la lógica de negocio determinista:

- `coaching` **consume** datos de `training`, `recovery`, `planning` y
  `analytics` únicamente a través de eventos de dominio o interfaces de
  aplicación expuestas — igual que cualquier otro módulo, sin privilegios
  especiales.
- `coaching` **no escribe** directamente en el estado de otros módulos:
  produce recomendaciones e insights como su propio agregado, nunca
  modifica agregados ajenos.
- Esta separación permite that la lógica determinista (registrar una
  actividad, calcular un readiness score, generar un calendario) sea
  íntegramente testeable y predecible sin depender de un modelo de IA, y
  que el propio modelo/proveedor de IA usado en `coaching` pueda
  evolucionar, cambiarse o incluso apagarse sin afectar la integridad del
  resto del sistema.

## Referencias

- [`docs/architecture/overview.md`](architecture/overview.md) — resumen
  ejecutivo y lista de bounded contexts.
- [`docs/architecture/ddd.md`](architecture/ddd.md) — resumen rápido de
  los patrones DDD.
- [`docs/architecture/offline-sync.md`](architecture/offline-sync.md) —
  borrador de la estrategia offline/sync, pendiente de decisión.
- [`docs/adr/`](adr/) — Architecture Decision Records puntuales.
- [`DECISIONS.md`](DECISIONS.md) — registro cronológico de decisiones
  técnicas ya tomadas.
