# Roadmap

> Roadmap por fases, desde la infraestructura hasta la primera beta.
> Cada fase declara objetivo, criterios de finalización (Definition of
> Done) y dependencias de fases anteriores. Las fases son secuenciales en
> su núcleo, pero algunas tareas pueden solaparse cuando no compartan
> dependencias directas.
>
> Estado de cada fase se marca como: ✅ Completada, 🚧 En curso, ⏳ Pendiente.

## Fase 0 — Fundamentos y estructura ✅

**Objetivo**: dejar el repositorio listo para desarrollar sin ambigüedad
sobre stack, arquitectura ni proceso, antes de escribir una sola línea de
lógica de negocio.

**Criterios de finalización**
- Monorepo inicializado con estructura backend/frontend/docs/infra/tests/scripts.
- Licencia propietaria aplicada.
- Repositorio remoto privado creado y enlazado (`origin`).
- `CODEOWNERS` configurado.
- Documentación base de arquitectura, estado, roadmap, decisiones y
  contribución (este set de documentos).

**Dependencias**: ninguna.

---

## Fase 1 — Infraestructura de desarrollo ⏳

**Objetivo**: pasar de manifiestos vacíos a un entorno de desarrollo
real y ejecutable, sin implementar todavía funcionalidad de negocio.

**Alcance**
- Elegir versiones concretas de dependencias backend (FastAPI, SQLAlchemy
  o equivalente, driver de base de datos) y actualizarlas en
  `pyproject.toml`; instalar en un entorno virtual.
- Bootstrap real de la app móvil con Expo (`npx create-expo-app` o
  equivalente) e instalación de dependencias declaradas en `package.json`.
- Elegir motor de base de datos (candidata: PostgreSQL) y motor de
  persistencia local en mobile (SQLite / WatermelonDB / Realm).
- Levantar `infra/docker/docker-compose.yml` con servicios reales
  (backend + base de datos, cache si aplica) y verificar que arrancan.
- Primer workflow de CI en `.github/workflows/` (lint + tests, aunque
  estén vacíos al principio).

**Criterios de finalización**
- `docker compose up` levanta un entorno local funcional.
- La app móvil arranca en un simulador/dispositivo mostrando una pantalla
  placeholder.
- CI ejecuta en cada push/PR (aunque no haya tests de negocio todavía).
- ADR correspondiente registrado en `DECISIONS.md` para cada elección de
  librería/motor.

**Dependencias**: Fase 0.

---

## Fase 2 — Shared Kernel (`platform/`) ⏳

**Objetivo**: construir los building blocks compartidos por todos los
módulos, sin los cuales ningún bounded context puede implementarse de
forma consistente.

**Alcance**
- `platform/domain`: `Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`.
- `platform/application`: contrato de `UnitOfWork`, interfaz de bus de
  eventos.
- `platform/infrastructure/persistence`: configuración base de acceso a
  datos (engine/sesión) y repositorio genérico.
- `platform/infrastructure/outbox`: implementación del Transactional
  Outbox (tabla de outbox, escritura atómica junto al agregado, proceso
  de despacho).
- `platform/infrastructure/messaging`: adaptador de bus de eventos interno.

**Criterios de finalización**
- Un agregado de prueba puede persistirse vía Unit of Work y su evento de
  dominio queda escrito en la tabla de outbox dentro de la misma
  transacción.
- Un proceso de despacho publica los eventos pendientes del outbox y los
  marca como enviados.
- Tests unitarios del shared kernel en `backend/tests/unit`.

**Dependencias**: Fase 1 (dependencias instaladas, base de datos elegida).

---

## Fase 3 — Identity ⏳

**Objetivo**: primer bounded context de negocio real: usuarios,
autenticación y dispositivos vinculados, base necesaria para que
cualquier otro módulo tenga un propietario de los datos y para que el
módulo `sync` pueda distinguir dispositivos.

**Criterios de finalización**
- Alta de usuario, autenticación básica y registro de dispositivo
  funcionando end-to-end (dominio → aplicación → infraestructura → API).
- Repository Pattern y Unit of Work del módulo implementados sobre el
  shared kernel de la Fase 2.
- Tests de integración del módulo.

**Dependencias**: Fase 2.

---

## Fase 4 — Training (módulo de referencia) ⏳

**Objetivo**: implementar `training` (running, ciclismo, gimnasio) como
módulo de referencia completo — sirve de plantilla para el resto de
bounded contexts de negocio.

**Criterios de finalización**
- Registro y consulta de actividades end-to-end: dominio, persistencia,
  API y una pantalla real en la app móvil (lista + detalle de actividad).
- Eventos de dominio relevantes (p. ej. `ActivityRecorded`) publicados vía
  outbox.
- Documentado como plantilla de referencia para las Fases 6 y 7.

**Dependencias**: Fase 3 (requiere usuario propietario de la actividad).

---

## Fase 5 — Offline-First y Sincronización ⏳

**Objetivo**: hacer que la app móvil funcione sin conexión y sincronice
con el backend y entre dispositivos.

**Alcance**
- Motor de persistencia local en `frontend/mobile/src/data/local`.
- Cola de cambios offline y motor de sincronización en
  `frontend/mobile/src/data/sync`.
- Módulo `sync` en el backend: recepción de cambios, resolución de
  conflictos, distribución a otros dispositivos del mismo usuario.
- Estrategia de resolución de conflictos decidida y documentada (ver
  `docs/architecture/offline-sync.md`).

**Criterios de finalización**
- Se puede registrar una actividad sin conexión y aparece sincronizada en
  otro dispositivo del mismo usuario al recuperar la conexión.
- Conflictos de escritura concurrente se resuelven según la estrategia
  documentada, sin pérdida silenciosa de datos.

**Dependencias**: Fase 4 (necesita datos de negocio reales que sincronizar).

---

## Fase 6 — Recovery y Planning ⏳

**Objetivo**: añadir los módulos de recuperación (sueño, HRV, fatiga,
readiness) y planificación (planes de entrenamiento, periodización,
calendario), reutilizando el patrón establecido en la Fase 4.

**Criterios de finalización**
- `recovery` y `planning` implementados end-to-end siguiendo la misma
  plantilla que `training`.
- `planning` puede consumir datos de `training` y `recovery` únicamente
  vía eventos de dominio o interfaces de aplicación expuestas, nunca
  accediendo directamente a sus repositorios.

**Dependencias**: Fase 5 (los datos de estos módulos también deben ser
offline-first y sincronizables).

---

## Fase 7 — Analytics y Coaching (IA) ⏳

**Objetivo**: estadísticas agregadas y entrenador basado en IA,
manteniendo la IA arquitectónicamente separada de la lógica determinista
(ver `ARCHITECTURE.md`).

**Criterios de finalización**
- `analytics` agrega métricas de los módulos de negocio ya implementados.
- `coaching` consume datos de dominio a través de puertos bien definidos
  y produce recomendaciones sin escribir directamente en el estado de
  otros módulos.
- Estrategia de evaluación/calidad de las recomendaciones documentada.

**Dependencias**: Fase 6 (necesita datos suficientes de training/recovery/
planning para generar recomendaciones significativas).

---

## Fase 8 — Integrations ⏳

**Objetivo**: conectar proveedores externos (Garmin, Strava, Whoop,
TrainingPeaks, Hevy) mediante la capa anticorrupción ya reservada en
`modules/integrations`.

**Criterios de finalización**
- Al menos un proveedor externo (candidato: Strava, por tener API pública
  bien documentada) integrado end-to-end: importación de actividades
  traducida al modelo de dominio de `training`.
- Patrón de adaptador documentado y replicable para el resto de
  proveedores.

**Dependencias**: Fase 4 (necesita el modelo de dominio de `training`
estable como destino de la traducción).

---

## Fase 9 — Hardening y Beta ⏳

**Objetivo**: cerrar los cabos sueltos de proceso y calidad antes de una
primera beta cerrada.

**Alcance**
- Actualizar a GitHub Pro (o equivalente) y aplicar el ruleset completo de
  `main` documentado en `docs/agent/OPEN_QUESTIONS.md`.
- Cobertura de tests de integración/e2e en `tests/` para los flujos
  críticos (alta de usuario, registro de actividad, sincronización).
- Revisión de seguridad básica (gestión de secretos, autenticación,
  permisos de API).
- Pulido de UX en los flujos principales de la app móvil.

**Criterios de finalización**
- CI en verde de forma consistente, incluyendo checks obligatorios en el
  ruleset de `main`.
- Flujo completo (alta → registro de actividad offline → sincronización →
  visualización de estadísticas) verificado manualmente y con tests
  automatizados.
- Primera beta cerrada distribuida a un grupo reducido de usuarios.

**Dependencias**: Fases 1–8 completas.
