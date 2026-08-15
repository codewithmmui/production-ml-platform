# Deployment

Run `docker compose up --build` from a clean checkout. The multi-stage API build trains a
deterministic bootstrap model and verifies both model and metadata artifacts before constructing the
non-root runtime image. This makes CI and tagged image publication independent of ignored local
files. For Kubernetes, replace `OWNER`, create secrets externally, and use
`helm upgrade --install ml-platform helm/production-ml-platform`. Production deployments should
replace the bootstrap model through an artifact init container or registry-aware loader, verify its
digest/signature, and use immutable image digests, managed PostgreSQL/Redis, TLS ingress,
PodDisruptionBudgets, and topology spread.
