# app/

Rutas de Expo Router (file-based routing).

- `_layout.tsx` - root layout, provee `AuthProvider`.
- `index.tsx` - redirige a `(app)`.
- `(auth)/` - `login`, `register`. Redirige a `(app)` si ya hay sesión.
- `(app)/` - shell autenticado. Redirige a `(auth)/login` si no hay sesión.
  `index.tsx` es una pantalla placeholder que confirma la sesión vía
  `GET /users/me`; las pantallas reales de `training` llegan en el resto
  de la Fase 4.
