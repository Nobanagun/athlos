# Athlos Mobile

App principal de Athlos: React Native + Expo + TypeScript, con Expo
Router para el enrutado basado en archivos. Disenada offline-first.

> Estado actual: bootstrap real (dependencias instaladas, Metro
> empaqueta sin errores) con navegacion y autenticacion JWT completas
> contra el backend real (registro, login, vinculacion de dispositivo,
> logout). Sin persistencia local offline todavia - motor por decidir
> (SQLite / WatermelonDB / Realm), fuera de alcance de este incremento
> (ver docs/DECISIONS.md).

## Estructura

```
mobile/
├── app/                    # Rutas de Expo Router - ver app/README.md
├── src/
│   ├── domain/               # Modelos de dominio del cliente (espejo del backend)
│   ├── data/
│   │   ├── local/              # Persistencia local / offline - pendiente (Fase 5)
│   │   ├── remote/              # httpClient.ts + identity.ts (registro/login/dispositivo)
│   │   └── sync/                # Motor de sincronizacion offline-first - pendiente (Fase 5)
│   ├── features/
│   │   └── auth/                 # AuthContext, useAuth
│   └── shared/                     # env.ts, deviceId.ts
└── assets/                          # Iconos, splash screens, fuentes
```

## Como ejecutar

```
cp .env.example .env    # y define EXPO_PUBLIC_API_URL
npm install
npm run typecheck
npm run lint
npm test
npm start                # requiere simulador/dispositivo real
```

## Siguiente fase (no incluida todavia)

- Persistencia local offline-first y motor de sincronizacion (Fase 5).
- Pantallas reales de `training` (lista + detalle de actividad) sobre
  el shell autenticado ya existente.
