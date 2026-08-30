# AGENTPAY PostgreSQL Development Environment (Phase 012)

## Executive Summary

This document specifies the setup, operation, environment configuration, health monitoring, and developer procedures for the **AGENTPAY PostgreSQL Development Environment** (`Phase 012`).

The development environment uses Docker Compose to run a containerized PostgreSQL 15+ database with persistent volume storage, health checks, and strict environment separation.

---

## 1. Development Architecture

```text
               Local Developer Workstation (Windows / Linux / macOS)
                                        │
                                        ▼
                   Docker Compose Stack (docker-compose.yml)
             ┌──────────────────────────┴──────────────────────────┐
             │                                                     │
             ▼                                                     ▼
┌─────────────────────────┐                            ┌──────────────────────┐
│  agentpay-postgres      │                            │  agentpay-redis      │
│  (postgres:15-alpine)   │                            │  (redis:7-alpine)    │
│  Port: 5432             │                            │  Port: 6379          │
│  Volume: postgres_data  │                            │  Volume: redis_data  │
└─────────────────────────┘                            └──────────────────────┘
```

---

## 2. Environment Configuration & Connection String

### Environment Variables (.env)

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_dev_pass
POSTGRES_DB=agentpay_dev
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres_dev_pass@localhost:5432/agentpay_dev?sslmode=disable
```

> [!CAUTION]
> Real production database credentials MUST NEVER be committed to source code or stored in `.env.example`.

---

## 3. Container Lifecycle Commands

### Start Database Service
```bash
docker compose up -d postgres
```

### Stop Database Service
```bash
docker compose stop postgres
```

### View Live Logs
```bash
docker compose logs -f postgres
```

### Check Container Status & Health
```bash
docker compose ps postgres
```

### Connect to Interactive PSQL Shell
```bash
docker exec -it agentpay-postgres psql -U postgres -d agentpay_dev
```

---

## 4. Health Check Mechanism

The PostgreSQL container executes an automated readiness probe using `pg_isready`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d agentpay_dev"]
  interval: 5s
  timeout: 5s
  retries: 5
```

- **Starting**: State transitions from `starting` to `healthy` once PostgreSQL accepts TCP connections and responds to `pg_isready`.
- **Backend Readiness**: Dependent applications must await the `healthy` container status before initiating database connection pools.

---

## 5. Persistence & Reset Procedures

### Persistence Invariant
Data persists across container restarts and recreations via the named Docker volume `postgres_data`.

### Intentional Development Reset Procedure
To reset the development database and destroy local development data:

1. **Stop & Remove Volumes**:
   ```bash
   docker compose down -v
   ```
2. **Re-initialize Stack**:
   ```bash
   docker compose up -d postgres
   ```

*Note: Destructive resets require explicit `-v` flags and are never executed automatically on application startup.*

---

## 6. Windows & PowerShell Compatibility

Developer commands are tested and verified for PowerShell on Windows:

```powershell
# Verify container status in PowerShell
docker compose ps

# Inspect logs
docker compose logs postgres --tail 50
```
