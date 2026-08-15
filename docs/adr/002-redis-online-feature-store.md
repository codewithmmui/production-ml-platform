# ADR 002: Redis online feature store

## Context
Entity features need millisecond keyed access and freshness control.
## Decision
Use Redis values with update timestamps and TTL behind an adapter.
## Alternatives
PostgreSQL-only access increases serving contention; Feast adds operational surface prematurely.
## Consequences
Simple low latency and replaceability; materialization consistency and cache recovery remain explicit duties.
