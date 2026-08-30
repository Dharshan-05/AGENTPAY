# AGENTPAY — 20: Model Artifact Integrity, Versioning & Drift Checks

## 1. Model Governance & Reproducibility

FRAUDGUARD ML model artifacts (`fraudguard_xgb_v1.4.2.bin`) are stored in secure object storage with SHA-256 integrity checksums. Every risk evaluation decision records the exact `model_version` used, enabling 100% reproducible historical auditing.

---

## 2. Drift Monitoring & Model Rollback

Feature distribution shifts and model prediction confidence drift are monitored in real time. If feature drift exceeds threshold limits, the system triggers an alert and supports single-command model artifact rollback.
