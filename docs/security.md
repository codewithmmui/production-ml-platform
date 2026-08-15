# Security

Threats include malicious API payloads, credential disclosure, dependency/image compromise, untrusted model deserialization, lateral movement, and sensitive telemetry. Mitigations include strict bounded Pydantic schemas, no raw customer logging, external secrets, non-root/read-only containers, dropped Linux capabilities, NetworkPolicy, minimal service accounts, dependency/secret/filesystem scans, and trusted pipeline-only joblib artifacts. Production should verify artifact digest/signature before deserialization, enforce TLS and authentication at the gateway, rotate credentials, generate SBOMs, and audit registry promotion.

Application and training environments use the official `mlflow-skinny` tracking client. The full
MLflow server remains isolated in its Compose service. This separation avoids pulling server-only
cryptographic and web dependencies into the API/training image and reduces its vulnerability and
runtime surface.
