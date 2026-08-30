# AGENTPAY — 45: Financial Data Retention, Archival & Legal Compliance Rules

## 1. Data Retention Policy

* **Financial Records (`payments`, `refunds`, `ledger_entries`)**: Retained in active PostgreSQL storage for 7 years minimum to comply with India RBI & GST financial regulations.
* **Audit Block Chains (`audit_events`)**: Retained indefinitely in append-only cold storage (S3 Glacier Object Lock).
* **Idempotency Records (`idempotency_records`)**: Purged automatically after 24 hours.
