# Tests

Esta carpeta contiene tests que cruzan servicios (integracion y e2e).
Los tests unitarios viven junto a cada codebase:

- Backend: `backend/tests/unit`
- Mobile: colocados junto a cada feature (pendiente de definir convencion
  al implementar la app).

## Subcarpetas

- `integration/` - tests de integracion entre modulos/backend y
  dependencias reales (base de datos, etc.).
- `e2e/` - tests end-to-end que ejercitan el flujo completo
  mobile -> backend.

> Sin tests implementados todavia; esta es solo la estructura inicial.
