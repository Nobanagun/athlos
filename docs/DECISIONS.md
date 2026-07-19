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
