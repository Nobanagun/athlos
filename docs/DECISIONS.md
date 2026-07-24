# Decisions Log

Registro cronológico de decisiones técnicas ya tomadas para Athlos. Cada
entrada documenta **qué** se decidió, **por qué** y **qué consecuencias**
tiene. Las decisiones de arquitectura más elaboradas tienen además su
propio ADR en [`docs/adr/`](adr/); este documento es el registro
cronológico completo, incluyendo decisiones de proceso y tooling que no
justifican un ADR aparte.

> Convención: nuevas decisiones se añaden al final, nunca se reescribe el
> historial. Si una decisión se revierte o cambia, se añade una entrada
> nueva que referencia a la anterior.

---

## 2026-07-19 — Stack de backend: Python + FastAPI

**Decisión**: el backend se construye en Python usando FastAPI.

**Motivo**: API moderna, tipado con Pydantic, soporte async nativo;
adecuado para la lógica de datos y la futura integración de IA
(`coaching`). Alternativas consideradas: Node.js/Express (mismo lenguaje
que el frontend) y Django (framework batteries-included).

**Consecuencias**: el entorno de desarrollo necesita Python 3.13+;
`backend/pyproject.toml` usa `hatchling` como build backend; el resto de
decisiones de dependencias (ORM, driver de base de datos) parten de este
stack.

---

## 2026-07-19 — Stack de frontend: React Native + Expo (principal) y Next.js (planificado)

**Decisión**: la app principal de Athlos es React Native + Expo +
TypeScript, con Expo Router para la navegación, diseñada offline-first.
Un dashboard web en Next.js + TypeScript queda **planificado pero no
implementado** en esta fase.

**Motivo**: el producto es ante todo una app móvil (paralelismo con
Garmin Connect/Strava/Hevy); un dashboard web de administración y
visualización avanzada tiene sentido pero no es crítico en esta fase.

**Consecuencias**: `frontend/mobile/` tiene la estructura completa
(incluido `data/sync` para offline-first); `frontend/web/` solo existe
como carpeta reservada con un README explicando que se implementará más
adelante (ver Fase 9+ implícita en `ROADMAP.md`, sujeta a repriorización).

---

## 2026-07-19 — Arquitectura: monolito modular con DDD, Repository, UoW, eventos de dominio y Transactional Outbox

**Decisión**: el backend es un monolito modular organizado por bounded
contexts (DDD), con Repository Pattern, Unit of Work, comunicación entre
módulos vía eventos de dominio, y Transactional Outbox para su
publicación fiable. La plataforma es offline-first con sincronización
multi-dispositivo, y el módulo de IA (`coaching`) está arquitectónicamente
separado de la lógica determinista.

**Motivo**: un solo desarrollador en esta fase no justifica el coste
operativo de microservicios; DDD con fronteras estrictas permite escalar
la complejidad de negocio (8 dominios: identity, training, recovery,
planning, coaching, analytics, sync, integrations) sin que el código se
vuelva un monolito no modular. El Transactional Outbox evita el problema
de doble escritura entre la base de datos y el bus de eventos.

**Consecuencias**: toda la estructura de `backend/src/athlos/modules/` y
`backend/src/athlos/platform/` deriva de esta decisión. Detalle completo
en [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 2026-07-19 — Instalación de Docker Desktop vía Homebrew

**Decisión**: se instala Docker Desktop (incluye Docker Compose v2) en la
máquina de desarrollo mediante `brew install --cask docker`.

**Motivo**: entorno de desarrollo local reproducible para el backend y
sus dependencias (base de datos, cache), requerido por el `ROADMAP.md`
(Fase 1).

**Consecuencias**: primer intento falló por permisos de `sudo` sobre
`/usr/local/bin` (propiedad de `root`); se resolvió ejecutando el comando
en una terminal interactiva real. Requiere además el primer arranque
manual de la app (`open -a Docker`) para completar la configuración de
`cli-plugins` y levantar el daemon. Verificado con `docker run
hello-world`.

---

## 2026-07-19 — Estructura del monorepo

**Decisión**: monorepo único con `backend/`, `frontend/` (`mobile/` +
`web/`), `docs/`, `infra/`, `tests/` (integración/e2e cross-servicio) y
`scripts/`.

**Motivo**: un solo repositorio simplifica la coordinación entre backend
y frontend en una fase temprana con un único desarrollador; los tests
unitarios viven junto a cada codebase (`backend/tests/`), mientras que la
carpeta `tests/` de nivel superior se reserva para integración y e2e
cross-servicio.

**Consecuencias**: todos los archivos de código fuente creados en esta
fase son placeholders (docstrings en Python, manifiestos sin instalar en
Node) — no hay imports de dependencias no instaladas, para evitar código
roto en el repositorio.

---

## 2026-07-19 — Licencia propietaria

**Decisión**: `LICENSE` propietaria, todos los derechos reservados.
Copyright © 2026 Alejandro Cutiño Torres. Prohibida la copia,
modificación, distribución, sublicencia, venta o uso del software sin
autorización expresa y por escrito del titular.

**Motivo**: Athlos es un producto propietario, no un proyecto de código
abierto.

**Consecuencias**: el archivo `LICENSE` no contiene datos personales
adicionales (sin email, sin dirección) más allá del nombre del titular.

---

## 2026-07-19 — Repositorio GitHub privado

**Decisión**: repositorio `Nobanagun/athlos` creado como **privado**, sin
README/.gitignore/licencia generados por GitHub (ya existían localmente),
remoto configurado como `origin`, rama por defecto `main`.

**Motivo**: el código y el diseño de producto no deben ser públicos en
esta fase.

**Consecuencias**: ver la decisión siguiente — el plan gratuito de GitHub
para repos privados no incluye rulesets/branch protection.

---

## 2026-07-19 — Identidad de commit del repositorio

**Decisión**: `git config user.email` fijado a nivel de repositorio (no
global) a `mallorcaale@gmail.com`; se reescribió el commit inicial con
`git commit --amend --reset-author` para aplicar el cambio.

**Motivo**: el commit inicial usó una identidad autogenerada por Git
(`usuario@hostname.local`) al no haber configuración global de
`user.name`/`user.email`.

**Consecuencias**: el cambio es local a este repositorio; otros
repositorios de la máquina no se ven afectados.

---

## 2026-07-19 — CODEOWNERS

**Decisión**: `.github/CODEOWNERS` asigna todo el repositorio (`*`) a
`@Nobanagun`, con una entrada explícita adicional protegiendo el propio
archivo `CODEOWNERS`.

**Motivo**: dejar preparada la asignación de propiedad de código para
cuando el ruleset de `main` pueda exigir revisión de code owners (ver
limitación de plan más abajo), y evitar que el propio archivo de
propiedad pueda modificarse sin que quede registrado como tal.

**Consecuencias**: ninguna todavía, hasta que se active
`require_code_owner_review` en el ruleset de `main` (bloqueado por plan,
ver siguiente entrada).

---

## 2026-07-19 — Protección de `main` bloqueada por plan GitHub Free; política de proceso compensatoria

**Decisión**: se intentó crear un ruleset de protección para `main`
(bloqueo de force push, bloqueo de borrado, PR obligatorio, conversaciones
resueltas, sin aprobación obligatoria de otra persona) vía `gh api`. La
API respondió `403: Upgrade to GitHub Pro or make this repository public
to enable this feature`. Se decidió **no** hacer público el repositorio
ni actualizar a Pro por ahora, y en su lugar documentar la limitación y
aplicar la política por disciplina de proceso: todo desarrollo en ramas
`feature/*`; `main` solo recibe cambios vía Pull Request salvo excepción
técnica explícitamente aprobada; nunca `force push`.

**Motivo**: GitHub Rulesets y la protección de rama clásica no están
disponibles en repositorios privados del plan gratuito (solo en públicos,
o en privados con GitHub Pro/Team/Enterprise). Mantener el repo privado
es más importante en esta fase que tener protección automatizada.

**Consecuencias**: la disciplina de `feature/*` + PR + no force-push
depende del cumplimiento manual (por el desarrollador y por cualquier
agente que opere en el repo) hasta que se actualice el plan. Documentado
en [`docs/agent/OPEN_QUESTIONS.md`](agent/OPEN_QUESTIONS.md). El JSON del
ruleset ya diseñado queda listo para aplicarse en cuanto se actualice el
plan (ver Fase 9 del `ROADMAP.md`).

---

## 2026-07-19 — Instalación y autenticación de GitHub CLI

**Decisión**: se instala `gh` (GitHub CLI) vía `brew install gh` (formula,
no cask) y se autentica de forma interactiva con `gh auth login` contra
la cuenta `Nobanagun`.

**Motivo**: necesario para crear y administrar el repositorio remoto
desde la línea de comandos (creación del repo, gestión de rulesets).

**Consecuencias**: a diferencia del cask de Docker, la instalación de la
formula `gh` no requirió `sudo` (el prefijo `/opt/homebrew/bin` pertenece
al usuario, no a `root`).

---

## 2026-07-19 — Migración de `httpx` a `httpx2` (dependencia de desarrollo de `TestClient`)

**Contexto**: al ejecutar `pytest` durante el bootstrap del backend
(Fase 1), apareció `StarletteDeprecationWarning: Using httpx with
starlette.testclient is deprecated; install httpx2 instead`. Se investigó
antes de actuar: el paquete original `httpx` no tiene ningún release
estable desde diciembre de 2024 (solo previews `1.0.dev1/2/3` hasta
septiembre de 2025); Pydantic asumió el mantenimiento bajo el nombre
`httpx2` en mayo de 2026 como continuación directa ("the '2' is a
versioning marker for the new stewardship, not a fundamental rewrite",
[github.com/pydantic/httpx2](https://github.com/pydantic/httpx2)).
Starlette (`testclient.py`, código fuente instalado) intenta `import
httpx2 as httpx` primero y solo cae a `httpx` con warning si `httpx2` no
está instalado. Se comprobó en `uv.lock` que `httpx` era **únicamente**
una dependencia directa nuestra en `[dependency-groups] dev` — ningún
paquete instalado (FastAPI, Starlette, Uvicorn) lo declaraba como
dependencia propia.

**Decisión**: sustituir `httpx~=0.28.1` por `httpx2~=2.7.0` en
`[dependency-groups] dev` de `backend/pyproject.toml`, sin mantener
ambas. No se requirió ningún cambio de código: `fastapi.testclient` y
`backend/tests/unit/test_bootstrap.py` solo importan `TestClient`, y
Starlette resuelve `httpx2`/`httpx` internamente sin exponer el detalle.

**Alternativas consideradas**:
- Mantener `httpx` y aceptar el warning permanentemente — descartado: no
  hay releases estables desde hace 19 meses, por lo que futuras
  vulnerabilidades no tendrían parche garantizado en el paquete original.
- Declarar ambas (`httpx` y `httpx2`) "por seguridad" — descartado por la
  propia regla de `CONTRIBUTING.md` (no mantener dos dependencias
  directas para el mismo propósito sin una razón técnica demostrada; aquí
  no la hay, nada más en el árbol de dependencias requiere `httpx`).
- Fijar una versión exacta (`==2.7.0`) — descartado en favor de
  `~=2.7.0` (permite parches `2.7.x`, coherente con el resto de pines del
  proyecto), evitando quedar congelados en un parche de seguridad futuro.

**Consecuencias**:
- El warning de deprecación desaparece; `uv run pytest -v` pasa limpio
  (2 tests, 0 warnings).
- Cadena de dependencias transitivas cambia: `httpx2` trae `httpcore2` y
  `truststore` (en vez de `httpcore` + `certifi`). `truststore` usa el
  almacén de certificados nativo del sistema operativo en lugar de un
  bundle de CA empaquetado (`certifi`) — sin impacto ahora (solo se usa
  en tests locales), pero es algo a revisar si en el futuro se ejecutan
  tests en contenedores mínimos sin almacén de certificados del SO
  configurado (Fase 1, infraestructura Docker).
- Ruff, mypy y pre-commit se re-ejecutaron completos tras el cambio: sin
  incidencias.

**Riesgo de adoptar un fork relativamente reciente**: `httpx2` se anunció
en mayo de 2026 (dos meses de antigüedad en el momento de esta decisión).
Es un fork con compromiso explícito de compatibilidad y mismo diseño que
`httpx`, mantenido por Pydantic (mismo proveedor que ya usamos para
`pydantic` en runtime), pero tiene menos recorrido en producción que el
`httpx` clásico. Al ser una dependencia de **desarrollo** (solo tests),
el radio de impacto de un eventual problema queda acotado al entorno de
CI/desarrollo, no a producción.

**Criterio para revisar o revertir esta decisión**: revertir a `httpx`
(o evaluar alternativas) si ocurre cualquiera de estos casos:
- `httpx2` deja de recibir releases durante un periodo prolongado (misma
  señal de alerta que motivó esta migración).
- Aparece una incompatibilidad real con `TestClient`/Starlette en una
  actualización futura de FastAPI/Starlette.
- El cambio de `certifi` a `truststore` causa fallos de verificación de
  certificados en el entorno de CI o en contenedores Docker (Fase 1).

---

## 2026-07-20 — Shared kernel (Fase 2): implementación inicial de `platform/`

**Decisión**: se implementan los building blocks del shared kernel
(`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`), los contratos
`UnitOfWork`/`EventBus`, `SqlAlchemyUnitOfWork` (implementación concreta,
síncrona), el modelo `OutboxMessage` y `dispatch_pending()`, y
`InMemoryEventBus`. Ningún módulo de negocio (`modules/`) se toca; no se
añade ninguna dependencia nueva.

**Unit of Work y sesiones síncronas**: se descarta async para esta fase.
FastAPI y psycopg3 soportan async, pero nada en Fase 2 lo exige, y async
habría requerido añadir `pytest-asyncio` sin un caso de uso real que lo
justifique todavía. Revisar cuando un módulo real (Fase 3+) demuestre
necesitar I/O concurrente de verdad.

**Algoritmo de `SqlAlchemyUnitOfWork.commit()`** (orden fijado
explícitamente, no incidental): 1) copiar (sin mutar) los eventos
pendientes de los agregados rastreados — una única vez, guardando esa
lista; 2) el agregado ya está en la sesión (responsabilidad de quien la
usa, vía `session.add()` antes de llamar a `commit()`); 3) escribir las
filas de `outbox` en la misma sesión; 4) `session.commit()` único; 5)
solo si el paso 4 tiene éxito, limpiar los eventos usando la **misma**
lista obtenida en el paso 1 (nunca se vuelve a consultar
`session.new/dirty/deleted` tras el commit, porque ese estado deja de ser
significativo una vez terminada la transacción). Si algo falla antes del
paso 4: `rollback()` y los eventos siguen intactos en memoria, porque
nunca se extrajeron (solo se copiaron) hasta que el commit tuvo éxito.

**`_tracked_aggregates()` como único punto de acceso a
`session.new/dirty/deleted`**: `SqlAlchemyUnitOfWork` no consulta esas
colecciones en ningún otro lugar. Es **suficiente para esta fase**: el
agregado de prueba siempre aparece en `session.new` en el mismo momento en
que registra su evento. **Limitación conocida**: este mecanismo no
detecta un agregado que registre un evento de dominio sin que ningún
atributo mapeado cambie (p. ej. un evento puramente notificacional). Si un
módulo real (Fase 3+) presenta ese caso, ese evento se perdería
silenciamente con el mecanismo actual — el cambio necesario (sustituir por
un registro explícito de agregados en la UoW) queda localizado a este
único método por diseño.

**Sin repositorio genérico en `platform/`**: no se pudo demostrar que
fuera imprescindible para los criterios de esta fase — `session.add()`
directo basta. Se añadirá en un módulo real (o se promoverá al shared
kernel) cuando un caso de uso concreto de Fase 3+ lo justifique.

**Tests contra SQLite en memoria, no PostgreSQL real**: evita depender de
que la Fase 1 de Docker esté cerrada. **Pendiente explícito**: SQLite
difiere de PostgreSQL en el manejo de tipos (`JSON`, `UUID`); el
comportamiento del outbox (en particular la columna `payload` JSON y las
claves `UUID`) debe re-validarse contra PostgreSQL real en cuanto
`infra/docker/docker-compose.yml` tenga un servicio de base de datos
activo (resto de la Fase 1 / Fase 3).

**Bus de eventos in-memory (`InMemoryEventBus`)**: no se usa Redis (ya
instalado como dependencia) porque no existe todavía ningún consumidor
cross-proceso real. `dispatch_pending()` recibe el mapeo
`event_type -> clase` como parámetro del llamador — el shared kernel no
conoce ningún tipo de evento concreto de ningún módulo.

**`target_metadata` de Alembic**: `migrations/env.py` ahora apunta a
`athlos.platform.infrastructure.persistence.database.Base`, que por ahora
solo registra `outbox_messages`. Sigue sin generarse ninguna migración
real (`alembic revision --autogenerate` no se ha ejecutado): eso requiere
un PostgreSQL real, pendiente del resto de la Fase 1.

**Consecuencias**: 19 tests unitarios nuevos en
`backend/tests/unit/platform/`, todos en verde; Ruff, mypy (`strict`, sin
`type: ignore` ni overrides de configuración) y `pre-commit` sin
incidencias. Se añadieron
`backend/tests/__init__.py`, `backend/tests/unit/__init__.py` y
`backend/tests/unit/platform/__init__.py` (no estaban en el plan
original) para que mypy pudiera distinguir los dos `conftest.py` del
árbol de tests como módulos distintos — pytest ya lo toleraba, mypy no.

---

## 2026-07-21 — Fase 3 (incremento 1): diseño inicial del módulo `identity`

**Decisión**: se implementa únicamente **identidad de usuario**, no
autenticación. `ROADMAP.md` describe la Fase 3 completa como "usuarios,
autenticación y dispositivos vinculados" — este incremento cubre solo la
existencia de un `User` con email y estado básico de cuenta. Sin login,
sin JWT/OAuth/refresh tokens/sesiones, sin almacenamiento de contraseñas
(ni siquiera hasheadas), sin proveedor externo de identidad, sin
dispositivos vinculados. `identity/interfaces/` e
`identity/infrastructure/` quedan sin tocar (ver más abajo).

**Modelo de dominio**: agregado `User(AggregateRoot[UserId])`;
`UserId`/`Email` como value objects (`platform.domain.ValueObject`);
`AccountStatus` como enum con **un único valor, `ACTIVE`** — no se añade
`DEACTIVATED` ni ningún otro estado hasta que exista un caso de uso real
que transicione la cuenta (evita una máquina de estados sin ningún
consumidor). `User.register(email)` es el único punto de entrada
previsto para crear usuarios; emite `UserRegistered`.

**Normalización de `Email`**: `strip()` + `lower()` aplicados **antes**
de validar la estructura (un único `@`, partes local/dominio no vacías).
Sin librería externa (`email-validator` u otra) — validación
estructural mínima, suficiente para esta fase; se revisará si el input
real por HTTP (fase posterior, con endpoints) expone casos que la
validación actual no cubra.

**`UserRegistered` con campos `str`, no `UserId`/`Email`**: consecuencia
directa del diseño del outbox de la Fase 2 —
`OutboxMessage.from_event()` usa `dataclasses.asdict()` asumiendo campos
JSON-primitivos; un `uuid.UUID` crudo en el payload rompería la
serialización JSON. Todo evento de dominio pensado para pasar por el
outbox debe declarar sus campos ya en tipos JSON-primitivos.

**⚠️ Unicidad de email no es todavía atómica**: `RegisterUserHandler`
comprueba duplicados vía `UserRepository.get_by_email()` antes de crear
el `User`, pero esto es una comprobación a nivel de aplicación, no una
garantía transaccional. Sin infraestructura real todavía (ver siguiente
punto), no existe ninguna restricción `UNIQUE` de base de datos. Dos
registros concurrentes con el mismo email podrían, en teoría, superar
ambos la comprobación antes de que cualquiera de los dos persista. **Esto
queda pendiente de cerrarse con una restricción `UNIQUE` real en la
tabla de usuarios cuando se implemente `identity/infrastructure`** (
incremento siguiente) — la comprobación actual es una mejora de UX
(mensaje de error claro), no la garantía dura.

**`RegisterUserHandler.handle()` devuelve solo `UserId`**, nunca el
agregado `User` — evita filtrar el objeto de dominio completo (y su
lista interna de eventos ya "gastados") fuera de la capa de aplicación.

**Infraestructura y HTTP deliberadamente fuera de este incremento**: sin
`SqlAlchemyUserRepository`, sin modelo ORM de `User`, sin migración real,
sin ningún endpoint. Los tests usan `InMemoryUserRepository` y
`FakeUnitOfWork` (dobles de prueba en `backend/tests/unit/modules/identity/application/_fakes.py`),
consistente con la filosofía de testing ya declarada en `ARCHITECTURE.md`.

**Consecuencias**: 14 tests unitarios nuevos en
`backend/tests/unit/modules/identity/`, todos en verde (33 en total en el
backend); Ruff, mypy (`strict`) y `pre-commit` sin incidencias. La
excepción de dominio se llama `EmailAlreadyRegisteredError` (no
`EmailAlreadyRegistered`) por la regla `N818` de Ruff (sufijo `Error`
obligatorio en nombres de excepción). Verificado explícitamente con
`grep`: `identity/` no importa de ningún otro módulo de `modules/`, y
`identity/domain`+`identity/application` no importan `sqlalchemy`,
`fastapi` ni `pydantic`.

**Pendiente**: `ROADMAP.md` Fase 3 sigue describiendo el alcance completo
(auth + dispositivos) sin anotar que se está partiendo en incrementos —
mismo tipo de nota pendiente que quedó para "repositorio genérico" en la
Fase 2.

---

## 2026-07-22 — Fase 3 (incremento 2): infraestructura de persistencia de `identity`

**Decisión**: se implementa `identity/infrastructure` con **mapeo
declarativo mediante subclase + `TypeDecorator`** para `UserId`/`Email`
(la Opción 1 de la comparación técnica previa a esta entrada). Se
descartaron: mapeo clásico (peor soporte de tipado en SQLAlchemy 2.x),
`composite()` (pensado para VOs multi-atributo, sobredimensionado para
un único valor envuelto) y modelo ORM separado con tipos primitivos
(rompía la detección de agregados de `SqlAlchemyUnitOfWork` sin tocar
`platform/`).

**Bloqueo real descubierto durante la implementación (no de
`platform/`)**: `User.register(email)` usa `cls(...)` internamente, pero
`RegisterUserHandler` (capa de aplicación) solo conoce la clase base
`User` — nunca `_MappedUser` (la subclase privada de infraestructura).
Esto significa que `User.register()` siempre construye un `User` sin
mapear, nunca un `_MappedUser`, y `session.add(user)` fallaba con
`UnmappedInstanceError`. Solución: `_MappedUser.from_domain(user)`, un
classmethod en `infrastructure/models.py` que envuelve el `User` ya
creado por la capa de aplicación en su forma persistible, trasladando
sus eventos de dominio pendientes. `SqlAlchemyUserRepository.add()`
llama a este método en vez de hacer `session.add(user)` directamente.
Verificado con una prueba manual antes de escribir los tests formales.
Ningún cambio en `platform/` fue necesario — el bloqueo estaba
enteramente dentro de `identity/infrastructure`.

**`EmailAlreadyRegisteredError` vs `IntegrityError`** — ambas conviven,
ninguna sustituye a la otra:

| | `EmailAlreadyRegisteredError` | `IntegrityError` |
|---|---|---|
| Origen | `RegisterUserHandler`, vía `get_by_email()` | La base de datos, al violar el `UNIQUE` de `users.email` |
| Cuándo | Antes de intentar persistir (una consulta previa) | Durante `commit()` (al escribir de verdad) |
| Naturaleza | Comprobación de aplicación, no atómica frente a condiciones de carrera | Garantía atómica y definitiva |
| Propósito | Buen UX (mensaje de dominio claro) en el caso sin concurrencia | Correctness real en el caso concurrente |

Probado explícitamente con dos escenarios distintos: `test_register_duplicate_email_raises_and_persists_nothing`
(camino feliz de la comprobación de aplicación) y
`test_integrity_error_rolls_back_transaction_completely` (se salta la
comprobación deliberadamente para forzar que el `IntegrityError` ocurra
dentro de `commit()`, verificando con una **sesión nueva** —no la que
falló— que ni el usuario ni su evento de outbox quedaron persistidos).

**Registro manual en `migrations/env.py`**: extender `Base` no basta
para que Alembic vea una tabla nueva — su módulo de modelos ORM tiene
que importarse explícitamente para que la clase declarativa se ejecute
antes de que `Base.metadata` se inspeccione. `migrations/env.py` ya
importaba el módulo del shared kernel (Fase 2); ahora también importa
`athlos.modules.identity.infrastructure.models`. **Esto es una
limitación de proceso, no un detalle puntual de este incremento**:
mientras no exista un mecanismo de descubrimiento automático de módulos
ORM, cada módulo futuro con infraestructura de persistencia propia debe
añadir aquí su propio import a mano — un olvido deja esa tabla invisible
para las migraciones sin ningún error visible. Documentado también en
`backend/migrations/README.md` para que sea lo primero que se vea al
tocar ese directorio.

**Sin migración real generada todavía**: sigue pendiente de un
PostgreSQL real (Fase 1). `Base.metadata` ya contiene `users` junto a
`outbox_messages`, lista para cuando se ejecute
`alembic revision --autogenerate`.

**Consecuencias**: 8 tests de integración nuevos en
`backend/tests/integration/identity/` (41 en total en el backend), todos
en verde; Ruff, mypy (`strict`, sin `type: ignore`) y `pre-commit` sin
incidencias. `platform/` queda sin ningún cambio (`git diff main --
backend/src/athlos/platform/` vacío) — la Opción 1 cumplió su promesa
principal. `TypeDecorator[UserId]`/`TypeDecorator[Email]` no dieron
ninguna fricción con `mypy --strict`, contra lo anticipado como riesgo en
el plan previo.

---

## 2026-07-23 — Bug real en el shared kernel: `AggregateRoot` y objetos reconstruidos por el ORM

**Contexto**: durante la revisión de la infraestructura de `identity`, se
descubrió empíricamente que cualquier `_MappedUser` cargado por
SQLAlchemy desde una fila (`get_by_id`, `get_by_email`, cualquier
consulta) carecía por completo del atributo `_domain_events` —
`.domain_events`, `.record_event()` y `.clear_domain_events()` lanzaban
`AttributeError`. Causa raíz: SQLAlchemy reconstituye instancias
cargadas vía `__new__` + población directa de atributos mapeados, **sin
pasar nunca por `__init__`** — que es donde `AggregateRoot.__init__` fija
`self._domain_events = []`. Verificado con una prueba manual antes de
tocar nada: en una sesión nueva (sin ambigüedad de mapa de identidad),
`fetched.domain_events` fallaba de inmediato.

**Decisión**: `AggregateRoot.domain_events`/`record_event()`/
`clear_domain_events()` tratan `_domain_events` ausente como "todavía sin
eventos" (`getattr`/`hasattr` con valor por defecto), en vez de asumir
que `__init__` siempre se ejecutó. `__init__` no cambia — sigue fijando
la lista explícitamente para la construcción normal; el cambio es
únicamente una red de seguridad para cuando `__init__` no se ejecuta.

**Alternativa descartada — `@reconstructor` de SQLAlchemy**: arreglaría
el problema en `_MappedUser` (infraestructura de `identity`) sin tocar
`platform/`, pero habría que **repetirlo en cada módulo futuro** que use
el mismo patrón de subclase declarativa (`training`, `recovery`, etc.),
dependiendo de que cada implementador se acuerde de añadirlo — exactamente
el mismo patrón de riesgo ("olvido silencioso módulo a módulo") ya
identificado y documentado para el registro manual en
`migrations/env.py`. La propiedad perezosa garantiza el invariante "todo
`AggregateRoot` tiene un ciclo de vida de eventos coherente" **por
diseño, una sola vez, en la propia clase**, en vez de por convención
repetida.

**Verificado antes de implementar** (no solo razonado): comportamiento
idéntico para construcción normal (confirmado con los 41 tests
existentes ejecutados con el diseño ya aplicado, sin ningún cambio de
resultado); coste de rendimiento insignificante (microbenchmark: ~1 ns
de diferencia por acceso sobre 200.000 iteraciones); y, revirtiendo el
fix temporalmente con `git stash`, se confirmó que los tests nuevos
fallan exactamente con el `AttributeError` original — no son falsos
positivos.

**Consecuencias**: 5 tests nuevos (46 en total en el backend): 4 en
`backend/tests/unit/platform/test_entity.py` (comportamiento normal sin
cambios, objeto creado vía `__new__` no revienta, `record_event`
inicializa bajo demanda, `clear_domain_events` es un no-op sin lista) y
1 de regresión en
`backend/tests/integration/identity/test_sqlalchemy_user_repository.py`
(`test_fetched_user_domain_events_does_not_crash`, con el flujo real:
repositorio + UoW reales + sesión nueva). Cambio localizado en
`platform/domain/entity.py` — ningún otro archivo de código tocado.

---

## 2026-07-24 — Fase 3 (incremento 3): `identity/interfaces` — `POST /users`

**Decisión**: primer endpoint HTTP real del proyecto, exponiendo
`RegisterUserHandler`. Establece el patrón de composición HTTP que
seguirán todos los módulos futuros con interfaz web — no existía ninguno
previo (`api/main.py` solo tenía `/health`).

**Ruta**: `POST /users`, sin prefijo `/identity` — los límites de módulo
son un detalle interno de organización del código, no algo que deba
filtrarse a la superficie pública de la API.

**`InvalidEmailError` sustituye a `ValueError` en `Email`**: se analizó
exhaustivamente el uso de `ValueError` en todo el codebase antes de
decidir — un único punto de origen (`Email.__post_init__`), y el camino
completo de `RegisterUserHandler.handle()` no tiene ningún otro punto que
pudiera lanzarlo por un motivo no relacionado. Aun así, se introdujo una
excepción de dominio específica, no por necesidad inmediata sino por el
mismo criterio ya aplicado al fix de `AggregateRoot`: capturar
`ValueError` en la capa HTTP sería seguro *hoy*, pero es una excepción
demasiado genérica para que ese patrón siga siendo seguro a medida que
`identity` (o cualquier módulo) crezca — un futuro `ValueError` no
relacionado, lanzado en el mismo camino de ejecución, se traduciría
erróneamente como "email inválido" sin que nada lo señale.
`InvalidEmailError` no hereda de `ValueError` — no hay nada en el
proyecto que dependa de capturar `ValueError` genéricamente para este
caso.

**Composición de dependencias**:
- `api/dependencies.py` (compartido, agnóstico de negocio): `get_session()`,
  `get_unit_of_work()`. Cualquier módulo futuro con persistencia los
  reutiliza directamente.
- `identity/interfaces/dependencies.py` (específico del módulo):
  `get_user_repository()`, `get_register_user_handler()`, construidos
  sobre los anteriores.
- **Bug encontrado y corregido durante la implementación**: crear el
  engine/`sessionmaker` a nivel de módulo en `api/dependencies.py`
  (código de importación, no perezoso) habría llamado a
  `get_database_url()` en el momento de **importar** el módulo — rompiendo
  la app entera (y los tests, que sustituyen `get_session` vía
  `app.dependency_overrides` pero necesitan poder importarla primero) en
  cualquier entorno sin `DATABASE_URL` configurada. Solucionado con
  `functools.lru_cache` sobre una función que construye el
  `sessionmaker` perezosamente, en el primer uso real, no al importar.

**`exception_handlers.py` vive en `identity/interfaces/`, no en `api/`**:
decisión ya justificada antes de implementar — un archivo centralizado en
`api/` tendría que importar las excepciones de dominio de cada módulo,
exactamente la dirección de acoplamiento que `ARCHITECTURE.md` prohíbe
entre módulos de negocio. `main.py` permanece como composition root puro:
solo crea la app, incluye el router de `identity` y llama a
`identity_exception_handlers.register(app)` — ninguna lógica de negocio,
ningún `@app.exception_handler` ni `Depends` se escribe directamente ahí.

**`config/settings.py` mínimo**: una única función, `get_database_url()`,
lee `DATABASE_URL` de `os.environ` — sin `pydantic-settings`, coherente
con cómo `migrations/env.py` ya lo hacía desde Fase 2/3.

**⚠️ `IntegrityError` por condición de carrera — deliberadamente no
traducido en este incremento**: dos peticiones concurrentes pueden ambas
superar la comprobación de `EmailAlreadyRegisteredError` antes de que
cualquiera comitee; la segunda choca contra el `UNIQUE` real y
`IntegrityError` se propaga sin traducir, resultando en `500`. No se
amplía el manejador de excepciones para cubrir este caso porque (a) el
alcance aprobado de este incremento solo cubría dos excepciones
concretas, y (b) traducir `IntegrityError` de forma genérica a `409`
tiene el mismo riesgo ya descartado para `ValueError`: esa excepción
también es demasiado amplia (cualquier violación de integridad de la
tabla, no solo el email, la dispararía). Verificado explícitamente con
un test que reproduce el escenario de forma determinista (sin hilos
reales): `test_race_condition_integrity_error_is_not_translated_and_surfaces_as_500`,
sustituyendo `get_by_email` por un doble que siempre informa "no existe
conflicto", dejando que la restricción real actúe dentro de `commit()`.

**Hallazgo adicional durante la implementación**: un engine SQLite
`:memory:` sin `poolclass=StaticPool` entrega una base de datos distinta
por hilo — invisible en los tests de integración anteriores (todo
síncrono, un solo hilo), pero rompía los tests de rutas porque
`TestClient` ejecuta las dependencias síncronas de FastAPI en un hilo del
pool de `anyio`. Corregido en
`backend/tests/integration/identity/conftest.py` (con
`connect_args={"check_same_thread": False}` también, necesario para
reutilizar la misma conexión entre el hilo de test y el hilo de la
petición).

**Consecuencias**: 5 tests de integración nuevos en
`backend/tests/integration/identity/test_routes.py` (51 en total en el
backend); Ruff, mypy (`strict`) y `pre-commit` sin incidencias. Se añadió
`[tool.ruff.lint.flake8-bugbear] extend-immutable-calls = ["fastapi.Depends"]`
a `pyproject.toml` — el idioma de inyección de dependencias de FastAPI
(`Depends(...)` como valor por defecto) es exactamente lo que la regla
`B008` de Ruff señala como antipatrón genérico; whitelisting explícito,
no una desactivación general de la regla.

---

## 2026-07-24 — Fase 3 (incremento 4): `identity` — autenticación JWT stateless

**Decisión**: se implementa autenticación con JWT stateless (sin
sesiones, sin tabla de tokens, sin refresh tokens, rotación ni
revocación en este incremento) — `POST /login`, la dependencia
`get_current_user` que valida el token, y `GET /users/me` como **único**
endpoint protegido de este incremento (alcance decidido explícitamente
para demostrar el ciclo completo login → token → acceso protegido
end-to-end, sin añadir más superficie protegida hasta que exista un
caso de uso real). Dispositivos vinculados quedan para el siguiente
incremento de la Fase 3, que sigue sin cerrarse.

**Modelo de credenciales — `password_hash` en el propio agregado
`User`, sin `Credentials` separado**: se descartó explícitamente una
entidad `Credentials` mientras exista un único método de login — mismo
criterio de minimalismo ya aplicado a `AccountStatus` (Fase 3,
incremento 1) y al repositorio genérico (Fase 2). `PasswordHash` es un
value object nuevo (`identity/domain/value_objects.py`) que envuelve el
hash ya calculado, sin ninguna validación propia — a diferencia de
`Email`, su forma la determina por completo el algoritmo que lo produjo
(detalle de infraestructura). `User.__init__`/`User.register()` ganan
un parámetro `password_hash: PasswordHash`.

**Reparto de responsabilidades del hashing — el dominio nunca hashea ni
verifica**: `User.register(email, password_hash)` recibe el hash ya
calculado; no conoce `PasswordHasher` ni ningún algoritmo concreto. Toda
la orquestación (hashear al registrar, verificar al hacer login) vive en
los handlers de `application` (mismo reparto ya establecido en
`RegisterUserHandler`, que construye `Email` y llama al repositorio) —
se descartó deliberadamente un diseño de "dominio rico" donde `User`
recibiera el hasher como colaborador, por ser un patrón nuevo sin
precedente en el resto del módulo y por desdibujar la frontera
dominio/aplicación ya establecida.

**`POST /users` (incremento 3) pasa a exigir `password`** —cambio con
ruptura deliberada del contrato ya en producción: `RegisterUserRequest`,
`RegisterUserCommand` y `RegisterUserHandler` ganan el campo; no se
introdujo un endpoint separado para fijar contraseña ni un estado
intermedio de "usuario sin credenciales". Se descartó explícitamente por
ser innecesario mientras exista un único flujo de alta.

**Política de fortaleza de contraseña — en `application`, no en el
Pydantic ni como Value Object**: `RegisterUserHandler` valida longitud
mínima (8 caracteres, `MIN_PASSWORD_LENGTH`) antes de hashear, lanzando
`WeakPasswordError` (dominio, HTTP 422) si no la cumple. Se descartó
tanto delegar la regla en `min_length` del DTO (habría quedado como
validación de formato HTTP, no como invariante de aplicación reutilizable
por otros caminos de entrada futuros) como no validar nada (Argon2id ya
hace inviable la fuerza bruta del hash, pero no protege un endpoint de
login contra contraseñas triviales probadas directamente). No existe un
Value Object `Password` para el texto plano — a diferencia de `Email`,
el password en claro nunca se persiste ni forma parte del estado del
agregado, solo transita por `application` camino del hasher.

**`InvalidCredentialsError` deliberadamente genérico**: `LoginUserHandler`
lanza la misma excepción tanto si el email no existe como si la
contraseña es incorrecta — evita enumeración de usuarios vía el mensaje
de error de login. Verificado explícitamente con un test que compara el
mensaje de ambos casos (`test_unknown_email_and_wrong_password_raise_the_same_generic_error`).
`LoginUserHandler` no usa `UnitOfWork` — un login exitoso no muta ningún
estado persistido (coherente con "stateless": no hay sesión que
escribir).

**Puertos nuevos en `application/ports.py`**: `PasswordHasher`
(`hash`/`verify`) y `TokenIssuer` (`issue`/`verify`), junto a
`UserRepository` — mismo patrón de puerto/adaptador ya establecido,
para que ni `domain` ni `application` importen `argon2` ni `PyJWT`
directamente.

**Hashing: Argon2id vía `argon2-cffi`**, sin tuning de parámetros
propio — se usan los valores por defecto de la librería, que ya hashea
con Argon2id (recomendación actual de OWASP), en
`identity/infrastructure/password_hasher.py`. Alternativas descartadas:
`bcrypt` (API más simple pero sin ser la recomendación vigente de
OWASP) y `passlib[bcrypt]` (capa de abstracción con historial de
mantenimiento más lento — mismo tipo de riesgo ya evaluado para `httpx`
en la entrada de 2026-07-19).

**JWT: `PyJWT` + `HS256`**, secreto simétrico único vía
`config.settings.get_jwt_secret()` (mismo patrón que `get_database_url()`
— lee `JWT_SECRET` de `os.environ`, lanza `RuntimeError` claro si falta).
`RS256` y gestión de claves asimétricas quedan descartados explícitamente
para este incremento — el puerto `TokenIssuer` deja la puerta abierta a
cambiar de algoritmo sin tocar dominio ni aplicación si hace falta más
adelante. **TTL fijo de 1 hora** (`_TOKEN_TTL` en
`jwt_token_issuer.py`), sin refresh token en este incremento — el TTL es
la única palanca de exposición ante un token filtrado mientras no exista
refresh/rotación; el propio código deja un comentario explícito para
bajarlo cuando el incremento de dispositivos añada refresh tokens.

**`get_current_user_id` usa `HTTPBearer(auto_error=False)`, no el
comportamiento por defecto**: sin este cambio, un `Authorization` header
ausente habría devuelto `403` (comportamiento por defecto de
`HTTPBearer` en FastAPI), inconsistente con `401` para token
inválido/expirado. Se comprueba `credentials is None` explícitamente y
se lanza el mismo `InvalidTokenError` en ambos casos — mismo código de
estado (`401`, con cabecera `WWW-Authenticate: Bearer`) para "sin token"
y "token inválido".

**Consecuencias**: 28 tests nuevos (79 en total en el backend, todos en
verde): dominio (`PasswordHash`, `User.register` actualizado),
aplicación (`RegisterUserHandler` con hash/política de contraseña,
`LoginUserHandler`), infraestructura sin base de datos
(`Argon2PasswordHasher`, `PyJwtTokenIssuer` — incluye el caso de un
token firmado con un secreto distinto y el de un token expirado,
construido con `jwt.encode` directamente para no depender del TTL real)
e integración HTTP completa (`test_login_and_me_routes.py`: login
correcto, credenciales incorrectas, email desconocido, `/users/me` con
token válido/ausente/inválido/firmado con otro secreto). Dependencias
nuevas en `pyproject.toml`: `argon2-cffi~=25.1.0` y `pyjwt~=2.13.0`
(versiones reales verificadas contra PyPI el mismo día). `JWT_SECRET`
añadido a `backend/.env.example` (comentado, con instrucción de generar
uno real vía `openssl rand -hex 32`, nunca comitear un valor real).
Ruff, mypy (`strict`, sin `type: ignore`) y `pytest` sin incidencias ni
warnings — los primeros intentos de tests con secretos JWT cortos
generaban `InsecureKeyLengthWarning` de PyJWT (mínimo recomendado de 32
bytes para HS256); corregido usando secretos de prueba suficientemente
largos en vez de silenciar el warning.

**Pendiente explícito**: `ROADMAP.md` Fase 3 sigue sin cerrarse —
dispositivos vinculados es el siguiente incremento antes de considerar
Fase 4. `Credentials` como agregado separado, refresh tokens,
rotación/revocación de tokens, y cualquier endpoint protegido más allá
de `GET /users/me` quedan fuera de alcance hasta que un caso de uso real
los justifique (mismo criterio de minimalismo aplicado en todo el
módulo).
---

## 2026-07-24 — Fase 3 (incremento 5): `identity` — dispositivos vinculados

**Decisión**: se implementa el registro de dispositivos vinculados a un
usuario — `POST /devices`, `GET /devices`, `DELETE /devices/{device_id}`,
los tres protegidos con el JWT del incremento 4. **Alcance
deliberadamente acotado a metadatos de dispositivo**: sin refresh
tokens, sin rotación, sin revocación ni ningún otro estado de sesión —
esa ampliación, si hace falta, es un incremento propio y explícito
futuro, no parte de este. Con esto, los tres criterios de finalización
de la Fase 3 listados en `ROADMAP.md` (alta de usuario, autenticación
básica, registro de dispositivo) quedan cubiertos.

**Modelo de dominio — `Device` como agregado propio, no una entidad hija
de `User`**: tiene ciclo de vida propio (vincular/desvincular) y
cardinalidad variable por usuario, a diferencia de `password_hash` (1:1
con `User`, ya resuelto sin agregado separado en el incremento 4). Único
campo de identificación aportado por el cliente: `device_id`
(`DeviceId`, value object que envuelve `uuid.UUID`, sin `.generate()` —
a diferencia de `UserId`, aquí el servidor nunca genera el valor, solo
lo registra). Metadatos deliberadamente mínimos: `device_id`, `user_id`,
`registered_at` — sin `platform` ni `name` en este incremento; se
ampliará mediante una migración específica si una necesidad real de
mostrar información al usuario lo justifica.

**Unicidad compuesta `(device_id, user_id)`, no `device_id` global**: el
mismo `device_id` físico puede vincularse a varios usuarios distintos
(dispositivo compartido, varias cuentas de prueba en el mismo
emulador). Registrar de nuevo el mismo par es idempotente: no crea una
fila nueva, no re-emite `DeviceLinked`, devuelve los datos del vínculo
ya existente.

**Identidad del agregado: `DeviceLinkId` (generado por el servidor), no
`device_id`**: consecuencia directa de la unicidad compuesta —
`AggregateRoot[T]` (`platform/domain/entity.py`) exige que `T`
identifique de forma única cada instancia, y con la unicidad compuesta
`device_id` por sí solo ya no lo garantiza (dos vínculos de usuarios
distintos podrían compartir `device_id` y compararse como "iguales" por
la igualdad de `Entity`, que se basa en el id). `DeviceLinkId` sigue el
mismo patrón que `UserId` (envuelve `uuid.UUID`, con `.generate()`).
**No se tocó `platform/`** — la ambigüedad se resolvió enteramente
dentro de `identity/domain`.

**`DeviceLinkId` es una identidad interna, nunca se expone por HTTP**:
`DELETE /devices/{device_id}` usa el `device_id` que el propio cliente
ya conoce (el que generó y envió al registrar), resuelto internamente
como `(user_id autenticado, device_id)` — el cliente no necesita
persistir un segundo identificador asignado por el servidor solo para
poder desvincularse. `DeviceResponse` tampoco incluye `DeviceLinkId`.

**`DeviceNotFoundError` deliberadamente genérica**: un `device_id` que
no existe y uno que existe pero pertenece a otro usuario devuelven el
mismo 404 — mismo criterio anti-enumeración ya aplicado a
`InvalidCredentialsError` en el incremento 4 (no revelar si un
`device_id` concreto está vinculado a otra cuenta).

**`DeviceLinked`/`DeviceUnlinked` vía outbox, simétrico a la creación**:
`Device.register()` y `Device.unlink()` registran su evento
correspondiente antes de que `UnlinkDeviceHandler` llame a
`devices.remove()` (`session.delete()` sobre la instancia mapeada ya
cargada). **Verificado explícitamente antes de implementar** (no solo
razonado): `SqlAlchemyUnitOfWork._tracked_aggregates()`
(`platform/infrastructure/unit_of_work.py`) ya incluye `session.deleted`
en `session.new | session.dirty | session.deleted`, así que un agregado
borrado se recoge exactamente igual que uno nuevo o modificado — su
evento pendiente se escribe en el outbox en la misma transacción que el
borrado real. **No se tocó `platform/`**: primer caso real en el
proyecto que ejercita esa rama del mecanismo, confirmando que el diseño
de Fase 2 ya la contemplaba sin necesitar cambios.

**`RegisterDeviceHandler` devuelve un DTO propio (`DeviceLinkResult`),
no el agregado `Device`**: laguna real detectada durante la
implementación, no prevista en el diseño — `DeviceResponse` necesita
`registered_at`, que la ruta no conoce por sí sola (a diferencia de
`device_id`, ya presente en el request) y que devolver solo `DeviceLinkId`
(mismo patrón que `RegisterUserHandler` devolviendo solo `UserId`) no
resuelve. Alternativas descartadas: devolver el agregado `Device`
completo (filtraría su lista de eventos ya "gastados" fuera de la capa
de aplicación, exactamente lo que el patrón de `RegisterUserHandler` ya
evita) y hacer una consulta adicional desde la ruta tras el `handle()`
(coste de una query extra por registro sin necesidad). `DeviceLinkResult`
vive en `application/register_device.py`, no en `interfaces/` — es el
contrato de retorno del handler, independiente de cualquier detalle
HTTP.

**Bug real encontrado durante la implementación (no una decisión de
arquitectura): pérdida de `tzinfo` en `registered_at` al pasar por
SQLite**. Verificado empíricamente antes de tocar nada: una columna
`DateTime` genérica en SQLite descarta el offset de zona horaria al
leer, incluso con `timezone=True` (probado explícitamente: sigue
perdiéndose). Esto rompía la idempotencia observable de `POST /devices`
— la segunda respuesta serializaba `registered_at` con un formato
distinto a la primera (con "Z" la instancia recién creada en memoria,
sin "Z" la releída de la base de datos). **Solución**: `UtcDateTimeType`,
un `TypeDecorator` más (mismo idioma ya usado en el módulo para
`UserId`/`Email`/`PasswordHash`/`DeviceId`) que normaliza a UTC-naive al
guardar y reconstruye `tzinfo=UTC` al leer — verificado con el mismo
script empírico que confirmó el bug, ahora con `before == after`.
`Device.registered_at` es así siempre timezone-aware, tanto recién
creado como releído de la base de datos.

**Consecuencias**: 33 tests nuevos (112 en total en el backend, todos en
verde): dominio (`Device`, `DeviceId`/`DeviceLinkId`), aplicación (los
tres handlers, con `InMemoryDeviceRepository` como doble de prueba),
infraestructura sin base de datos no aplica aquí (a diferencia del
incremento 4, no hay lógica de hashing/tokens que aislar) pero sí
infraestructura con SQLite real (incluida la restricción `UNIQUE`
compuesta y el roundtrip de `registered_at`), y los tres endpoints HTTP
con idempotencia, aislamiento entre usuarios y los casos 401/404. Ruff,
`ruff format`, mypy (`strict`) y `pre-commit` sin incidencias. Ningún
cambio en `platform/` (`git diff main -- backend/src/athlos/platform/`
vacío) — tanto la ambigüedad de identidad del agregado como el borrado
con evento se resolvieron enteramente dentro de `identity/`.

**Con este incremento, los criterios de finalización de la Fase 3 en
`ROADMAP.md` quedan cubiertos** (alta de usuario, autenticación básica y
registro de dispositivo end-to-end; Repository Pattern y Unit of Work
del módulo sobre el shared kernel; tests de integración). `ROADMAP.md`
sigue marcando la fase `⏳` — el cierre formal del marcador es una
decisión de proceso pendiente, no tomada en este incremento.

---

## 2026-07-24 — `UserId` se promueve al shared kernel (`platform/domain`)

**Contexto**: al empezar a diseñar la Fase 4 (`training`), surgió la
primera necesidad real de que un módulo de negocio distinto de
`identity` referencie al propietario de un registro (`Activity`
pertenece a un usuario). `UserId` vivía en `identity/domain`, pero
`ARCHITECTURE.md` prohíbe que un módulo dependa directamente del dominio
de otro ("ningún módulo accede directamente al repositorio o las tablas
de otro módulo... toda comunicación cruzada pasa por eventos de dominio
o interfaces de aplicación explícitamente expuestas") — importar
`identity.domain.value_objects.UserId` desde `training.domain` habría
violado esa regla tal como está escrita hoy.

**Decisión**: `UserId` se traslada a `platform/domain/user_id.py`, junto
al resto de building blocks del shared kernel (`Entity`, `AggregateRoot`,
`ValueObject`, `DomainEvent`). **`UserId` no es un concepto exclusivo del
bounded context `identity`** — es un identificador transversal que
cualquier módulo con datos propiedad de un usuario necesita (`training`,
`recovery`, `planning`, y en general cualquier módulo futuro), igual que
`Entity`/`AggregateRoot` no pertenecen a ningún módulo de negocio
concreto. Que `identity` sea el módulo que primero definió `User` (el
agregado) no hace de `UserId` (el identificador) una responsabilidad
suya — `identity` sigue siendo la única autoridad sobre *quién* es un
usuario (alta, autenticación, dispositivos); el resto de módulos solo
necesitan poder decir "esto pertenece al usuario X" sin conocer nada más
de `identity`.

**Alternativas descartadas**:
- Cada módulo define su propio tipo de identificador de usuario (p. ej.
  `training.domain.OwnerId`), desacoplado de `identity` por completo —
  aislamiento más estricto en la letra de `ARCHITECTURE.md`, pero
  introduce un patrón nuevo que cada módulo futuro tendría que repetir
  (Nº de tipos de "esto es un UUID de usuario" creciendo linealmente con
  el número de módulos), sin ninguna garantía de coherencia entre ellos
  más allá de compartir la forma `uuid.UUID`.
- Dejar `UserId` en `identity/domain` y que `training` lo importe
  directamente — más simple hoy, pero formaliza justo el acoplamiento
  entre bounded contexts que la regla de frontera de `ARCHITECTURE.md`
  existe para evitar.

**Migración, sin cambiar comportamiento**: `identity/domain/value_objects.py`
deja de definir `UserId`; todo el código de `identity` (dominio,
aplicación, infraestructura, interfaces) y sus tests actualizan su
import a `athlos.platform.domain.user_id`. `DeviceId`/`DeviceLinkId`
**no** se mueven — son específicos de `Device`, un concepto propio de
`identity`, no transversales como `UserId`. El test dedicado de la
value object (`test_user_id.py`) se traslada de
`tests/unit/modules/identity/domain/` a `tests/unit/platform/`,
coherente con su nueva pertenencia. Verificado que el comportamiento no
cambia: los mismos 112 tests, todos en verde, sin ninguna reescritura de
aserciones.

**Consecuencias**: ningún cambio de comportamiento observable — `UserId`
sigue siendo exactamente el mismo value object (envuelve `uuid.UUID`,
`.generate()` para IDs nuevos), solo cambia su ubicación e import.
`training` (y cualquier módulo futuro) puede referenciar `UserId` vía
`platform/`, exactamente igual que ya depende de `AggregateRoot`/
`UnitOfWork`, sin crear una dependencia hacia `identity`. Ruff, `ruff
format` y mypy (`strict`) sin incidencias tras la migración completa.
