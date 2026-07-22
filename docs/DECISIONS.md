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
