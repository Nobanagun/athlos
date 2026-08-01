# Project State

> Última actualización: 2026-08-01
> Este documento es la fuente de verdad sobre el estado real del proyecto.
> Debe actualizarse cada vez que cambie algo significativo (stack, estructura,
> fase actual). Si este documento contradice el código, el código manda —
> pero la contradicción debe corregirse aquí de inmediato.

## Estado actual

Fase 1 (bootstrap del backend, PR #1), Fase 2 (shared kernel de
`platform/`, PR #2) y **Fase 3 (`identity`, PR #3-#6) completadas**.
Cinco incrementos: (1) dominio + aplicación (`User`, `UserId`,
`Email`, `AccountStatus` solo `ACTIVE`, `UserRegistered`,
`UserRepository`, `RegisterUserHandler`); (2) infraestructura de
persistencia real (`SqlAlchemyUserRepository`, mapeo declarativo de
`User` vía subclase + `TypeDecorator` para `UserId`/`Email`, restricción
`UNIQUE` de email real); (3) `identity/interfaces` — primer endpoint HTTP
real del proyecto, `POST /users`; (4) **autenticación JWT stateless** —
`User` gana `password_hash` (Argon2id vía `argon2-cffi`), `POST /users`
ahora exige contraseña, `POST /login` emite un JWT (`PyJWT`/HS256, TTL de
1h, sin refresh/rotación/revocación) y `GET /users/me` es el primer
endpoint protegido, resuelto vía la dependencia `get_current_user`; (5)
**dispositivos vinculados** — nuevo agregado `Device` (identidad propia
`DeviceLinkId`, generado por el servidor; `device_id` lo aporta el
cliente, único por `(device_id, user_id)`, no globalmente), `POST
/devices`, `GET /devices` y `DELETE /devices/{device_id}` protegidos con
el mismo JWT, registro idempotente, eventos `DeviceLinked`/
`DeviceUnlinked` vía outbox (el borrado incluido, sin tocar
`platform/`). Con este incremento, los tres criterios de finalización de
la Fase 3 declarados en `ROADMAP.md` quedan cubiertos — alta de usuario,
autenticación básica y registro de dispositivo end-to-end, Repository
Pattern/Unit of Work sobre el shared kernel, tests de integración.
**Revisados y aprobados: la Fase 3 se marca aquí como completada.** El
marcador de fase en `ROADMAP.md` (`⏳` → `✅`) se actualiza como paso
separado, no incluido en esta revisión.

**Corrección puntual en el shared kernel**: se encontró y arregló un bug
real en `AggregateRoot` (`platform/domain/entity.py`) — un agregado
reconstruido por SQLAlchemy desde una fila (no construido en Python)
carecía de `_domain_events` y `.domain_events`/`record_event()`/
`clear_domain_events()` lanzaban `AttributeError`. Ver `DECISIONS.md`
para el análisis completo, la alternativa descartada y la verificación
empírica previa a implementar.

**Fase 4 (`training`) en curso — no cerrada todavía**. Backend completo
end-to-end (dominio, aplicación, persistencia, API) para los tres
deportes (`RunningActivity`/`CyclingActivity`/`GymActivity`,
independientes entre sí), más un cliente móvil de solo lectura (lista +
detalle de actividades). De los tres criterios de finalización de
`ROADMAP.md`: alta/consulta de actividades end-to-end y publicación de
`ActivityRecorded` vía outbox ya están **verificados con tests**
(incluido un test end-to-end del outbox, mismo patrón que `identity`);
la documentación como plantilla de referencia se cierra con esta misma
actualización.

**Validación manual completada — en Expo Web, no en iOS/Android
nativo**. El simulador iOS no está disponible en la máquina de
desarrollo (solo Command Line Tools, sin Xcode completo); se validó en
su lugar levantando backend + Expo con `--web` (`app.json` gana `web`
en `platforms` **solo de forma temporal**, revertido al cerrar la
validación). Checklist verificado end-to-end contra el backend real:
registro, login, persistencia de sesión tras recargar, logout, login
posterior, navegación `(auth)`↔`(app)`, listado de actividades (vacío y
con datos creados vía API), apertura de detalle, y el estado de error
de `Activities` con el backend detenido a propósito. **Tres bugs reales
encontrados y corregidos durante esta validación** (ver `DECISIONS.md`,
entradas del 2026-08-01):
1. **CORS**: sin `CORSMiddleware`, el navegador bloqueaba `POST
   /users` — nunca hacía falta antes porque el único cliente era
   React Native nativo, sin modelo de origen de navegador.
   `CORSMiddleware` ahora se registra condicionalmente, solo con
   orígenes explícitos por variable de entorno, nunca `"*"`.
2. **`expo-secure-store` sin implementación en Web** —
   `src/shared/secureStorage.ts`/`secureStorage.web.ts` (nuevos)
   resuelven la plataforma vía Metro, sin ramas `Platform.OS` en el
   código de negocio; iOS/Android siguen usando `expo-secure-store` sin
   cambios.
3. **Mensaje de error de login incorrecto ante fallo de red** —
   `login.tsx` mostraba "Invalid email or password." también cuando el
   servidor era inaccesible; ahora distingue `401` real, `TypeError`
   (red) y error inesperado.

**Bloqueo real restante antes del cierre formal, no ya de CORS/storage/
mensaje de error (resueltos)**: validación en iOS/Android — simulador
o dispositivo real — sigue sin ejecutarse. Ver `DECISIONS.md` (entradas
de Fase 4, incrementos 1-5 y 6, y las tres entradas del 2026-08-01) para
el detalle completo de decisiones.

**152 tests en total en el backend, todos en verde** (112 de
`identity`/`platform` + 40 de `training`) — **sin test automático para
el middleware de CORS**, verificado solo manualmente
(`curl`, preflight `OPTIONS` incluido). En el móvil: 16 tests
(`httpClient`, `AuthContext`, cliente de `training`) — **sin test
dedicado para `secureStorage.ts`/`secureStorage.web.ts` ni para la
distinción de errores en `login.tsx`**, ambos verificados solo
manualmente; `tsc --noEmit` y `eslint` limpios, `expo export
--platform ios` genera un bundle real de 1124 módulos sin errores.

Ver [`ROADMAP.md`](ROADMAP.md) para las fases siguientes y
[`docs/agent/OPEN_QUESTIONS.md`](agent/OPEN_QUESTIONS.md) para
limitaciones conocidas (protección de rama pendiente de GitHub Pro).

## Stack tecnológico aprobado

| Área | Tecnología | Estado |
|---|---|---|
| Backend | Python 3.13 + FastAPI 0.139.2 (uv) | Dependencias instaladas y fijadas, sin lógica de negocio |
| Frontend móvil (principal) | React Native + Expo + TypeScript + Expo Router | Bootstrap real hecho (auth JWT, cliente de `training` de solo lectura) — en rama, pendiente de merge; validado manualmente en Expo Web, iOS/Android nativo pendiente |
| Frontend web (dashboard/admin) | Next.js + TypeScript | Elegido, **no implementado**, fase futura |
| Persistencia local (mobile, offline-first) | Por decidir (SQLite / WatermelonDB / Realm) | Pendiente |
| Base de datos backend | Por decidir (candidata: PostgreSQL) | Pendiente |
| Infraestructura local | Docker + Docker Compose | Instalados en la máquina de desarrollo; sin servicios activos aún |
| Control de versiones | Git + GitHub (repo privado) | Configurado |
| CI/CD | GitHub Actions (planeado) | No implementado |
| Licencia | Propietaria, todos los derechos reservados | Aplicada |

## Arquitectura elegida

Monolito modular en el backend, organizado por bounded contexts siguiendo
Domain-Driven Design, con Repository Pattern, Unit of Work, eventos de
dominio y Transactional Outbox. Cliente móvil offline-first con
sincronización multi-dispositivo. El entrenador de IA (`coaching`) está
arquitectónicamente separado de la lógica determinista del resto de
módulos. Detalle completo en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Estructura del repositorio

```
athlos/
├── backend/                # Monolito modular Python/FastAPI (DDD)
│   └── src/athlos/
│       ├── modules/         # 8 bounded contexts (ver ARCHITECTURE.md)
│       ├── platform/         # Shared kernel (UoW, outbox, domain base)
│       ├── api/               # Composición de la app (FastAPI)
│       └── config/             # Settings (placeholder)
├── frontend/
│   ├── mobile/              # React Native + Expo (app principal)
│   └── web/                 # Next.js (reservado, no implementado)
├── docs/                    # Este documento y el resto de la documentación
├── infra/                   # Docker (placeholder, sin servicios activos)
├── tests/                   # Tests de integración/e2e cross-servicio
├── scripts/                 # Scripts de soporte (placeholder)
├── .github/CODEOWNERS       # @Nobanagun propietario de todo el repo
└── LICENSE                  # Propietaria
```

## Estado por área

### Backend

- Estructura de carpetas de los 8 módulos (bounded contexts) creada, cada
  uno con capas `domain/application/infrastructure/interfaces`. **6 de 8
  módulos siguen siendo placeholders con docstring** (`recovery`,
  `planning`, `coaching`, `analytics`, `sync`, `integrations`).
- **`identity` (Fase 3, incrementos 1-5)**: `domain/` gana `PasswordHash`
  (value object, sin validación propia), `User` con `password_hash`,
  `WeakPasswordError`/`InvalidCredentialsError`/`InvalidTokenError`
  (incremento 4, además de `InvalidEmailError` del incremento 3), y el
  agregado `Device` (incremento 5, identidad `DeviceLinkId` generada por
  el servidor, campos `device_id`/`user_id`/`registered_at`,
  `DeviceNotFoundError`). `application/` gana los puertos
  `PasswordHasher`/`TokenIssuer`/`DeviceRepository`,
  `RegisterUserHandler` actualizado (hashea y valida fortaleza mínima de
  8 caracteres), `LoginUserHandler` (sin `UnitOfWork` - solo lectura), y
  `RegisterDeviceHandler`/`ListUserDevicesHandler`/`UnlinkDeviceHandler`
  (incremento 5; registro idempotente por `(device_id, user_id)`).
  `infrastructure/` gana `Argon2PasswordHasher` (Argon2id vía
  `argon2-cffi`), `PyJwtTokenIssuer` (HS256, TTL de 1h), la columna
  `password_hash` en `_MappedUser`, y (incremento 5) `_MappedDevice`
  (tabla `devices`, `UNIQUE(device_id, user_id)`) con
  `SqlAlchemyDeviceRepository` y `UtcDateTimeType` (normaliza
  `registered_at` a UTC-naive al guardar y reconstruye `tzinfo=UTC` al
  leer - SQLite descarta el offset de zona horaria incluso con
  `timezone=True`); el resto (`SqlAlchemyUserRepository`, restricción
  `UNIQUE` sobre `users.email`) sin cambios desde el incremento 2.
  **`interfaces/`**: `POST /users` (incremento 3) exige `password`
  desde el incremento 4; `POST /login` y `GET /users/me` (incremento 4);
  `POST /devices`/`GET /devices`/`DELETE /devices/{device_id}`
  (incremento 5, protegidos con el mismo JWT) — `routes.py`,
  `dependencies.py`, `schemas.py` (Pydantic, solo aquí), y
  `exception_handlers.py` (traduce `InvalidEmailError`→422,
  `EmailAlreadyRegisteredError`→409, `WeakPasswordError`→422,
  `InvalidCredentialsError`→401, `InvalidTokenError`→401,
  `DeviceNotFoundError`→404; deja `IntegrityError` de condición de
  carrera sin traducir, propaga como 500 — decisión deliberada, ver
  `DECISIONS.md`).
- **`training` (Fase 4, incrementos 1-5) — primer módulo de negocio de
  referencia**: `domain/` con tres agregados completamente
  independientes (`RunningActivity`/`CyclingActivity`/`GymActivity`, en
  sus propios subpaquetes `running/`/`cycling`/`gym/`, sin base común ni
  herencia entre ellos), value objects compartidos en la raíz del
  módulo (`ActivityId`, `Duration`/`Distance` en SI — metros/segundos,
  ambos estrictamente positivos), el `Protocol` `ActivitySummary`
  (`id`/`user_id`/`sport`/`started_at`, único contrato estructural entre
  los tres deportes) y el evento genérico `ActivityRecorded`.
  `GymActivity` es deliberadamente mínimo (sin desglose de ejercicios).
  `application/` tiene un handler y un repositorio por deporte
  (`RegisterXActivityHandler`, `GetXActivityHandler`) más
  `ListUserActivitiesHandler` (única excepción cross-sport, orquesta los
  tres repositorios y fusiona en Python). `infrastructure/` tiene tres
  tablas separadas (`running_activities`/`cycling_activities`/
  `gym_activities`, mismo patrón `_MappedX` + `TypeDecorator` que
  `identity`) y reutiliza `UtcDateTimeType`, promovido a
  `platform/infrastructure/persistence/` en este mismo incremento (ver
  entrada siguiente). `interfaces/` expone
  `POST /activities/{running,cycling,gym}` (`201`),
  `GET /activities` (listado cross-sport, DTO mínimo) y
  `GET /activities/{sport}/{id}` (detalle completo por deporte), todos
  protegidos con el JWT ya existente de `identity`;
  `ActivityNotFoundError`→404 (genérico, mismo criterio anti-enumeración
  que `DeviceNotFoundError`). Ver `DECISIONS.md` para el detalle
  completo de decisiones y alternativas descartadas.
- **`platform/` (shared kernel) ya tiene implementación real** (Fase 2):
  `Entity`/`AggregateRoot`/`ValueObject`/`DomainEvent` (dominio puro, sin
  SQLAlchemy ni Pydantic); `UserId` (identificador transversal,
  trasladado desde `identity/domain` — ver `DECISIONS.md`);
  `UnitOfWork`/`EventBus` (contratos); `SqlAlchemyUnitOfWork` (concreta,
  síncrona, con el algoritmo de commit documentado en `DECISIONS.md`);
  `OutboxMessage` + `dispatch_pending()` (Transactional Outbox);
  `InMemoryEventBus`; `UtcDateTimeType` (`infrastructure/persistence/`,
  trasladado desde `identity/infrastructure` durante la Fase 4 — mismo
  criterio que `UserId`, evita repetir el bug de `tzinfo` en SQLite ya
  corregido una vez). Sin repositorio genérico (no se justificó
  todavía). Tests en `backend/tests/unit/platform/`.
- Gestor de dependencias: `uv`, con `.python-version` (3.13) y `uv.lock`
  commiteado. `pyproject.toml` declara dependencias reales y fijadas
  (`fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `psycopg`, `redis`,
  `pydantic` en runtime; `pytest`, `httpx2`, `ruff`, `mypy`, `pre-commit`
  en dev — ver `DECISIONS.md` para la justificación de cada versión).
- `backend/src/athlos/api/main.py` es el composition root (sin lógica de
  negocio): expone `GET /health`, el router de `identity` y ahora
  también el de `training`, cada uno con su propio registro de
  manejadores de excepciones. `api/dependencies.py` (nuevo, compartido,
  agnóstico de negocio):
  `get_session()`/`get_unit_of_work()`, con inicialización perezosa del
  engine (`functools.lru_cache`) para que importar el módulo nunca
  requiera `DATABASE_URL`. `config/settings.py`: lee `DATABASE_URL` y
  `JWT_SECRET` de entorno (sin `pydantic-settings`), y ahora también
  `get_cors_allowed_origins()` — `CORSMiddleware` se registra en
  `main.py` solo si hay orígenes configurados, nunca `"*"` (ver
  `DECISIONS.md`, 2026-08-01).
- Ruff, mypy (modo `strict`, sin excepciones) y pytest configurados en
  `pyproject.toml` y en verde; `pre-commit` instalado y validado contra
  un `git commit` real.
- Alembic configurado (`alembic.ini`, `migrations/env.py`,
  `script.py.mako`); `target_metadata` apunta a la `Base` del shared
  kernel, que ahora registra `outbox_messages`, `users`, `devices` **y
  las tres tablas de `training`**. Sigue sin generarse ninguna migración
  real — requiere PostgreSQL real, pendiente del resto de la Fase 1.
  **Registro manual obligatorio**: cada módulo con infraestructura
  propia debe añadir su import en `migrations/env.py` a mano — no hay
  descubrimiento automático (ver `DECISIONS.md` y
  `backend/migrations/README.md`).
- Sin base de datos ni Redis en ejecución — los drivers están instalados
  pero no hay ningún servicio real levantado (eso es Fase 1, sección de
  infraestructura Docker, todavía pendiente). Los tests de `platform/`,
  `identity` y `training` corren contra SQLite en memoria; **pendiente
  re-validar contra PostgreSQL real** (outbox desde Fase 2, la
  restricción `UNIQUE` de `identity`, y ahora también las tres tablas de
  `training`).

### Frontend

- **mobile/**: bootstrap real hecho (Expo instalado, `expo export`
  genera un bundle real sin errores) — **en rama, sin mergear a
  `main` todavía**. Expo Router con grupos `(auth)`/`(app)`;
  `AuthContext` (`src/features/auth/`) con almacenamiento seguro (sin
  refresh tokens — un `401` fuerza logout), vinculación de dispositivo
  tras login (tolerante a fallos de red/HTTP, no bloquea el login).
  **Almacenamiento diferenciado por plataforma**:
  `src/shared/secureStorage.ts` (iOS/Android, `expo-secure-store`) y
  `secureStorage.web.ts` (Web, `localStorage` sin cifrar — Web no es
  plataforma de producción soportada todavía), resueltos por Metro sin
  ramas `Platform.OS` en el código de negocio (ver `DECISIONS.md`,
  2026-08-01). **`login.tsx` distingue credenciales inválidas (`401`)
  de fallo de red (`TypeError`) de error inesperado**, en vez de un
  único mensaje genérico (mismo `DECISIONS.md`). Cliente de `training`
  de solo lectura: `src/domain/training.ts` (unión discriminada por
  `sport`), `src/data/remote/training.ts` (mapea DTO snake_case →
  dominio camelCase), pantallas
  `app/(app)/activities/{index,[sport]/[id]}.tsx` (lista + detalle,
  estado local de carga/error, sin hook compartido ni gestión de estado
  global). 16 tests, `tsc`/`eslint` limpios. **Validado manualmente en
  Expo Web** (registro, login, persistencia de sesión, logout,
  navegación, listado, detalle, estados de carga/error/vacío) contra el
  backend real. **Sin validar todavía en un simulador o dispositivo
  iOS/Android real** — pendiente, sin Xcode completo disponible en la
  máquina de desarrollo actual. Persistencia local (`data/local`) y
  sincronización (`data/sync`) siguen sin implementar — motor por
  decidir, Fase 5.
- **web/**: solo existe como carpeta reservada con un README explicando
  que se implementará en una fase posterior.

### Infraestructura

- Docker Desktop y Docker Compose v2 instalados y verificados en la
  máquina de desarrollo.
- `infra/docker/docker-compose.yml` es un placeholder sin servicios
  activos (comentarios de ejemplo para backend/postgres/redis).
- Sin CI configurado (no existe ningún workflow en `.github/workflows/`).
- Repositorio GitHub privado creado (`Nobanagun/athlos`), con `CODEOWNERS`
  aplicado. **Protección de rama pendiente**: GitHub Free no permite
  rulesets/branch protection en repos privados (ver `OPEN_QUESTIONS.md`).

## Próximo objetivo

**Fase 4 (`training`) en curso, no cerrada todavía.** Backend completo
(152 tests) y cliente móvil de solo lectura (16 tests) implementados;
de los tres criterios de finalización de `ROADMAP.md`, los dos
verificables con tests ya lo están (actividades end-to-end,
`ActivityRecorded` vía outbox) y la documentación como plantilla de
referencia se cierra con esta actualización. **Validación manual
completada en Expo Web** contra el backend real (registro, login,
persistencia de sesión, logout, navegación, listado, detalle, estados
de carga/error/vacío), con tres bugs reales encontrados y corregidos en
el proceso (CORS, `secureStorage` en Web, mensaje de error de login —
ver `DECISIONS.md`, 2026-08-01). **Queda un único bloqueo antes del
cierre formal**: validar en iOS/Android — simulador o dispositivo real
— no ejecutable en la máquina de desarrollo actual (sin Xcode
completo), requiere intervención directa.

Sin relación de bloqueo con el cierre de la Fase 4, sigue pendiente:
(1) mergear las ramas de `training` (backend y cliente móvil) y el
bootstrap móvil a `main`; (2) tests automáticos para el middleware de
CORS y para la distinción de errores en `login.tsx` (verificados solo
manualmente hasta ahora); (3) el resto de la Fase 1 (CI, servicios
Docker reales) y, con Postgres real disponible, generar la primera
migración real y re-validar outbox + restricciones `UNIQUE`
(`users.email`, `devices(device_id, user_id)`) contra él; (4)
traducción de `IntegrityError` por condición de carrera en `identity`,
deliberadamente fuera de alcance hasta ahora (ver `DECISIONS.md`). Ver
`ROADMAP.md`.
