# ADR 004: Separate training and serving images

## Context
Training has different entrypoints, privileges and resource patterns from inference.
## Decision
Build separate non-root images from one package.
## Alternatives
One universal image simplifies builds but enlarges attack surface and scheduling ambiguity.
## Consequences
Clear runtime contracts and independent scaling at modest build duplication cost.
