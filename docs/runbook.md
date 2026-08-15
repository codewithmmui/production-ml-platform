# Production runbook

## API unhealthy or model failed to load

**Symptoms:** liveness/readiness failure, `model_loaded 0`, 503 predictions. **Diagnose:** `kubectl -n ml-platform describe pod -l app=ml-api`; `kubectl -n ml-platform logs deploy/ml-api --tail=200`; compare artifact digest and `/model/info`. **Causes:** missing/corrupt artifact, memory pressure, incompatible feature schema. **Recover:** stop rollout; restore the last signed artifact/image digest; restart deployment. **Verify:** `/health` and `/ready` are 200, `model_loaded 1`, known-canary prediction matches expected version.

## Redis unavailable

**Symptoms:** online lookup 503, feature-store latency/errors. **Diagnose:** `redis-cli -u "$REDIS_URL" ping`; inspect Redis endpoints/events and saturation. **Causes:** failover, connection exhaustion, eviction, DNS. **Recover:** fail over/scale Redis, restore network/DNS, rematerialize expired features. Explicit-feature prediction remains available. **Verify:** PING succeeds and a test entity round trip is fresh.

## PostgreSQL unavailable

**Symptoms:** materialization/training failures; serving with request features remains healthy. **Diagnose:** `pg_isready -d "$DATABASE_URL"`; inspect connections, disk and replica lag. **Causes:** connection saturation, storage, migration, failover. **Recover:** fail over, expand storage/pool safely, roll back migration; replay idempotent materialization. **Verify:** read/write probe and training-set row/hash reconciliation succeed.

## High prediction latency

**Symptoms:** P95 alert, timeout/error increase. **Diagnose:** correlate CPU/memory/throttling, request batch size, feature-store histogram and pod-level latency. **Causes:** oversized batches, Redis delay, CPU throttling, model regression. **Recover:** cap/reject batch, scale replicas, fix dependency, or roll back model. **Verify:** P95 remains within SLO for 15 minutes and error rate normalizes.

## Drift alert

**Symptoms:** `drift_score`/report crosses configured threshold. **Diagnose:** inspect per-feature KS/PSI/JS, data-quality failures and upstream release calendar. **Causes:** real behavior change, seasonality, instrumentation defect. **Recover:** fix instrumentation first; otherwise label representative outcomes and run challenger workflow. Never promote without gates. **Verify:** new reference is approved, challenger report is recorded, post-deploy drift/quality is stable.

## Bad model deployment / rollback

**Symptoms:** outcome KPI or canary degrades despite healthy service. **Diagnose:** compare production alias/version, dataset hash, feature schema, prediction distribution and challenger report. **Recover:** point MLflow `production` alias to last verified version or deploy its immutable image digest; restart/canary. Do not delete the bad version—archive it with incident metadata. **Verify:** `/model/info` shows rollback version and canary/outcome monitors recover.

## Retraining failure

**Symptoms:** job failure/no candidate. **Diagnose:** inspect validation output, dataset hash, dependency status, MLflow/artifact permissions and resource usage. **Causes:** schema drift, corrupt batch, registry outage, insufficient memory. **Recover:** quarantine invalid data, restore dependency or adjust declared resources; rerun idempotently with the same dataset hash. **Verify:** run records full lineage and reaches an explicit promote/reject decision.
