# Contributing

Reglas de proceso para desarrollar en Athlos — aplican por igual a un
desarrollador humano y a cualquier agente de IA (incluido Claude Code)
que opere sobre este repositorio.

## Flujo de desarrollo

1. Partir siempre de `main` actualizado (`git pull origin main`).
2. Crear una rama `feature/*` para el cambio (ver convención de nombres
   abajo).
3. Hacer commits siguiendo la convención descrita más abajo.
4. Ejecutar los tests relevantes localmente antes de abrir el Pull
   Request.
5. Abrir un Pull Request contra `main` en GitHub.
6. Revisar el propio diff de principio a fin antes de fusionar (ver
   sección de checklist pre-merge).
7. Fusionar el PR (no hay revisión obligatoria de otra persona mientras
   haya un único desarrollador — ver `docs/agent/OPEN_QUESTIONS.md`).

## Ramas `feature/*` obligatorias

- **Todo desarrollo se realiza en ramas `feature/*`.** Nombre recomendado:
  `feature/<módulo-o-área>-<descripción-corta>`, por ejemplo
  `feature/training-activity-repository`.
- Para cambios de documentación o proceso, es aceptable `docs/*` o
  `chore/*` como prefijo alternativo, siguiendo el mismo principio: nunca
  se trabaja directamente sobre `main`.

## No trabajar directamente sobre `main`

`main` solo recibe cambios mediante Pull Request, **excepto** cuando una
limitación técnica del plan GitHub Free impida temporalmente ese flujo
(ver `docs/agent/OPEN_QUESTIONS.md`) y el cambio haya sido aprobado
explícitamente por el propietario del repositorio. Esta excepción no es
una puerta trasera de conveniencia: se reserva para casos ya acordados
explícitamente, no para saltarse el flujo por rapidez.

## Tests antes de cada merge

Antes de fusionar cualquier PR a `main`:
- Ejecutar la suite de tests relevante (`backend/tests` para cambios de
  backend; tests de `frontend/mobile` cuando existan; `tests/integration`
  o `tests/e2e` si el cambio cruza servicios).
- Si el cambio no tiene tests que lo cubran y debería tenerlos, añadirlos
  antes de fusionar, no después.
- Revisar el diff completo, no solo el resumen de archivos cambiados.

## No usar `force push`

Nunca se hace `git push --force` (ni `--force-with-lease`) sobre ninguna
rama compartida, y en particular nunca sobre `main`. Si una rama
`feature/*` necesita reescribirse (rebase, squash), hacerlo solo si la
rama es de un único autor y nadie más la ha construido encima.

## Convención de commits

Se sigue el estilo [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>: <descripción corta en imperativo>
```

Tipos usados en este repositorio:

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad de negocio |
| `fix` | Corrección de un defecto |
| `docs` | Cambios solo de documentación |
| `chore` | Tareas de mantenimiento, tooling, configuración |
| `refactor` | Cambio de estructura interna sin alterar comportamiento |
| `test` | Añadir o corregir tests, sin cambiar lógica de producción |

Ejemplos ya usados en el historial: `chore: initialize Athlos monorepo
structure`, `chore: add proprietary LICENSE`, `chore: add CODEOWNERS`,
`docs: document main branch protection limitation on GitHub Free`.

El mensaje debe explicar el **porqué** cuando no sea obvio, no repetir el
diff. Sin cuerpo extenso salvo que la decisión no esté ya registrada en
`DECISIONS.md` (en cuyo caso, mejor registrarla allí y mantener el commit
corto).

## Flujo recomendado para Claude Code (o cualquier agente)

Al retomar trabajo en este repositorio tras una pausa larga, en este
orden:

1. Leer `docs/PROJECT_STATE.md` — qué existe y qué no, ahora mismo.
2. Leer `docs/ROADMAP.md` — en qué fase se está y qué sigue.
3. Leer `docs/DECISIONS.md` — decisiones ya tomadas, para no
   reabrirlas ni contradecirlas sin motivo nuevo.
4. Leer `docs/agent/OPEN_QUESTIONS.md` — limitaciones conocidas y
   políticas activas (p. ej. protección de rama pendiente).
5. Antes de implementar, confirmar la fase/tarea concreta con quien pida
   el trabajo si no está ya explícita en el roadmap.
6. Trabajar en una rama `feature/*`, nunca sobre `main`.
7. Al terminar un cambio significativo (nueva fase completada, decisión
   de arquitectura tomada, limitación descubierta), **actualizar**
   `PROJECT_STATE.md` y/o `DECISIONS.md` en el mismo PR — no dejarlo para
   después.
8. No usar `force push`. No fusionar sin que los tests relevantes pasen.
9. No implementar funcionalidad más allá de lo pedido explícitamente para
   la tarea en curso, aunque el roadmap mencione pasos futuros — el
   roadmap informa el orden, no autoriza adelantarse sin que se pida.
10. Antes de crear una nueva dependencia, justificar por qué es necesaria
    y comprobar si una ya existente cubre el caso de uso.
11. Antes de modificar una decisión arquitectónica registrada en
    `DECISIONS.md`, documentar el motivo del cambio y su impacto.
