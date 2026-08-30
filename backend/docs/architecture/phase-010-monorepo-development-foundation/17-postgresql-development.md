# AGENTPAY — 17: Local Containerized PostgreSQL 14+ Development Environment

## 1. Local Postgres Service Config

* **Image**: `postgres:15-alpine`
* **Container Name**: `agentpay-postgres`
* **Port**: `5432`
* **Healthcheck**: `pg_isready -U postgres -d agentpay_dev`
* **Init Scripts**: Automatically mounts `infrastructure/postgres/init-rls.sql` to enable RLS extension functions.
