# Deployment

Build local artifacts before the image, then run `docker compose up --build`. For Kubernetes, replace `OWNER`, create secrets externally, and use `helm upgrade --install ml-platform helm/production-ml-platform`. Production deployments should use immutable digest-pinned images, managed PostgreSQL/Redis, TLS ingress, PodDisruptionBudgets, topology spread, and an artifact init container or registry-aware loader.
