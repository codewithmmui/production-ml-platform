# Monitoring

Prometheus scrapes `/metrics`; Grafana is provisioned from repository JSON. Alert on readiness failure, sustained error ratio, P95 latency budget, model-loaded zero, and drift threshold. Labels are bounded to endpoint, error type, class, operation, and model version. Never label by customer or request ID.
