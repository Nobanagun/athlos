# Open Questions / Limitaciones conocidas

## Protección de la rama `main` (pendiente)

- La rama `main` **no tiene ruleset ni branch protection** aplicado. GitHub
  Rulesets y la protección de rama clásica no están disponibles en
  repositorios **privados** bajo el plan **GitHub Free**; requieren
  GitHub Pro (cuenta individual) o Team/Enterprise (organización).
- **Todo desarrollo deberá realizarse en ramas `feature/*`.**
- **La rama `main` solo recibirá cambios mediante Pull Request**, excepto
  cuando una limitación técnica del plan GitHub Free impida temporalmente
  ese flujo y el cambio haya sido aprobado explícitamente.
- **No usar `force push`** bajo ninguna circunstancia, con o sin
  protección de rama activa.
- **Antes de fusionar** cualquier rama `feature/*` a `main`: ejecutar los
  tests y revisar el diff completo.

Cuando se actualice a GitHub Pro, retomar la creación del ruleset
documentado para `main` (bloqueo de force push, bloqueo de borrado,
PR obligatorio, conversaciones resueltas, y checks de CI en cuanto
existan).
