# ADR 003: MLflow tracking and registry

## Context
Experiments and promoted artifacts require lineage and lifecycle metadata.
## Decision
Use MLflow runs and model aliases, with local-file tracking as a developer fallback.
## Alternatives
Custom tables omit ecosystem support; managed platforms reduce portability.
## Consequences
Portable tracking and registry semantics; production requires durable database/object storage and access control.
