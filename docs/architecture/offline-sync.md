# Offline-first y sincronizacion (borrador)

## Requisitos

- La app movil debe funcionar completamente sin conexion.
- Los cambios realizados offline deben sincronizarse cuando haya red,
  tanto con el backend como entre los distintos dispositivos de un mismo
  usuario.

## Decisiones pendientes

- Motor de almacenamiento local en el cliente (SQLite / WatermelonDB /
  Realm).
- Estrategia de resolucion de conflictos (last-write-wins, CRDTs, vector
  clocks, o resolucion manual segun el tipo de dato).
- Protocolo de sincronizacion (polling vs. push, formato del payload de
  cambios, idempotencia).

> Este documento se ampliara durante la fase de diseno detallado del
> modulo `sync` (backend) y `data/sync` (mobile).
