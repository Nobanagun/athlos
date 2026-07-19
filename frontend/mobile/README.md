# Athlos Mobile

App principal de Athlos: React Native + Expo + TypeScript, con Expo
Router para el enrutado basado en archivos. Disenada offline-first.

> Estado actual: solo estructura de carpetas y manifiestos. No se ha
> ejecutado `npm install` / `npx expo install` ni se ha decidido aun la
> libreria concreta de persistencia local (candidatas: SQLite, WatermelonDB,
> Realm).

## Estructura

```
mobile/
├── app/                 # Rutas de Expo Router (file-based routing)
├── src/
│   ├── domain/           # Modelos de dominio del cliente (espejo del backend)
│   ├── data/
│   │   ├── local/         # Persistencia local / offline
│   │   ├── remote/        # Clientes de API hacia el backend
│   │   └── sync/          # Motor de sincronizacion offline-first
│   ├── features/          # Modulos de UI por dominio (training, recovery, ...)
│   └── shared/            # Componentes, hooks y utilidades compartidas
└── assets/                # Iconos, splash screens, fuentes
```

## Siguiente fase (no incluida todavia)

- Bootstrap real con Expo (`npx create-expo-app` o equivalente) e
  instalacion de dependencias.
- Eleccion de la libreria de persistencia local y el motor de sync.
- Implementacion de la primera feature end-to-end.
