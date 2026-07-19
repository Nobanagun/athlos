# Platform (Shared Kernel)

Building blocks compartidos por todos los modulos:

- `domain/` - Entity, AggregateRoot, ValueObject, DomainEvent base.
- `application/` - contratos compartidos: Unit of Work, bus de eventos.
- `infrastructure/persistence/` - configuracion base de acceso a datos y
  repositorios genericos.
- `infrastructure/outbox/` - implementacion del patron Transactional
  Outbox para publicar eventos de dominio de forma fiable.
- `infrastructure/messaging/` - adaptador del bus de eventos / broker.
