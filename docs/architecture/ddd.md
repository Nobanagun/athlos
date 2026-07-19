# Patrones DDD en el backend

- **Entity / Aggregate Root / Value Object** - bloques base de modelado
  de dominio, definidos en `platform/domain`.
- **Repository Pattern** - cada modulo expone interfaces de repositorio en
  su capa de dominio/aplicacion; las implementaciones concretas viven en
  `infrastructure/`, manteniendo el dominio libre de detalles de
  persistencia.
- **Unit of Work** - coordina cambios sobre varios repositorios dentro de
  una unica transaccion, garantizando consistencia.
- **Domain Events** - los modulos se comunican entre si publicando y
  reaccionando a eventos de dominio, evitando dependencias directas.
- **Transactional Outbox** - los eventos de dominio se escriben en la
  misma transaccion que el cambio de estado que los origina y se publican
  de forma asincrona, evitando el problema de doble escritura (dual write).

> Detalle de implementacion pendiente: estos patrones estan documentados
> como contrato arquitectonico; el codigo concreto se anadira en la
> siguiente fase.
