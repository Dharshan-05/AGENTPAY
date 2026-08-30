# AGENTPAY Database Environment Management (Phase 016)

## Executive Summary

This document specifies the database environment separation matrix, configuration safety guards, test isolation mechanisms, and secret protection controls across execution environments for **AGENTPAY** (`Phase 016`).

---

## 1. Environment Classification Matrix

```text
==================================================
ENVIRONMENT MATRIX
==================================================

Development
Database: Local PostgreSQL Container (agentpay-postgres)
Secrets: Local development defaults allowed (.env / .env.example)
Isolation: Local workstation / docker network

Test
Database: Isolated Test PostgreSQL (AGENTPAY_TEST_DATABASE_URL)
Secrets: Fixture / mock test credentials
Production/Staging Access: BLOCKED by automated safety guard

Staging
Database: Dedicated Staging Managed Cloud Database
Secrets: Staging Secret Manager
Production Access: BLOCKED by network & credentials isolation

Production
Database: High-Availability Production PostgreSQL Cluster
Secrets: Production Secret Manager / IAM Credentials
Unsafe Defaults: BLOCKED (Default password, localhost host, debug mode)
```

---

## 2. Environment Safety Guards (`app/core/config.py`)

### Production Environment Safety Guards
When `APP_ENV=production` (`Environment.PRODUCTION`):
1. **Debug Mode Prohibition**: `debug=True` raises `ValueError("DEBUG mode cannot be enabled in PRODUCTION environment.")`.
2. **Wildcard CORS Prohibition**: `CORS_ALLOWED_ORIGINS=["*"]` raises `ValueError("Wildcard origin '*' is prohibited in PRODUCTION environment.")`.
3. **Unsafe Development Passwords**: Passwords matching `"postgres_dev_pass"`, `"postgres"`, `"admin"`, or `"password"` raise `ValueError`.
4. **Localhost Host Guard**: `POSTGRES_HOST="localhost"` or `"127.0.0.1"` (without an explicit `DATABASE_URL`) raises `ValueError`.

### Test Environment Safety Guard
When `APP_ENV=test` (`Environment.TEST`):
- Any connection URL containing production or staging keywords (`prod`, `production`, `staging`, `rds.amazonaws.com`, `database.azure.com`) is blocked immediately:
  ```python
  raise ValueError("Test environment cannot execute against PRODUCTION or STAGING database.")
  ```

---

## 3. Secret Isolation & Redaction

- Sensitive database fields (`postgres_password`, `database_url`, `effective_database_url`) are encapsulated in `SecretStr`.
- Diagnostic output APIs (`safe_summary`, `repr()`, structured logs, OpenAPI schema, error exceptions) mask sensitive credentials as `"[REDACTED]"`.
