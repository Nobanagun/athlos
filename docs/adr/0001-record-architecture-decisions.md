# 1. Registrar las decisiones de arquitectura

## Estado

Aceptado

## Contexto

Necesitamos registrar las decisiones de arquitectura significativas de
Athlos: que se decidio, por que y que alternativas se consideraron.

## Decision

Usaremos Architecture Decision Records (ADR), en el formato propuesto por
Michael Nygard. Cada decision se documenta en un archivo numerado dentro
de `docs/adr/`.

## Consecuencias

Las decisiones futuras (eleccion de base de datos, libreria de
persistencia local, estrategia de sincronizacion, etc.) deben registrarse
como nuevos ADR en lugar de discutirse solo de forma informal.
