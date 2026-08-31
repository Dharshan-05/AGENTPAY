# AGENTPAY — Supabase PostgreSQL Integration Guide

This document details how to integrate **Supabase PostgreSQL** as the managed cloud database infrastructure for AGENTPAY, preserving local Docker PostgreSQL fallback capabilities and zero secret leakage.

---

## 1. Architectural Overview

```text
Browser (Client)
   │
   ▼ (REST / HTTP)
Next.js Frontend (:3000)
   │
   ▼ (REST / HTTP API)
FastAPI Backend Gateway (:8000)  ── [JWT Auth / RBAC / AgentGuard / FraudGuard / XAI]
   │
   ▼ (SQL / asyncpg via SQLAlchemy 2.0)
Supabase PostgreSQL Managed Cloud DB (:5432 / :6543)
```

### Core Security & Architectural Principles
1. **FastAPI is Authoritative**: All frontend requests route through the FastAPI gateway. The Next.js client never directly connects to Supabase database ports or tables.
2. **Backend Authentication & Governance Preserved**: Zero-trust JWT tokens, RBAC permissions, AgentGuard policies, FraudGuard risk decisions, and transaction audit trails remain in FastAPI.
3. **Secret Isolation**: `SUPABASE_SERVICE_ROLE_KEY` and database credentials (`DATABASE_URL`) are strictly backend-only. Never expose database credentials to Next.js or browser JavaScript.
4. **Transparent Driver Support**: SQLAlchemy 2.0 AsyncEngine automatically normalizes connection strings starting with `postgresql://` or `postgres://` into `postgresql+asyncpg://` at runtime.

---

## 2. Supabase Project Setup

### Step 1: Provision Supabase Project
1. Log in to [Supabase Console](https://supabase.com/dashboard) and create a new project.
2. Store your database password in a secure password manager.
3. Note your project reference ID (`[YOUR-PROJECT-REF]`) and region (`[REGION]`).

### Step 2: Connection String Formats

Supabase provides two primary PostgreSQL connection modes:

* **Direct Connection (Port 5432)** — Best for running Alembic schema migrations:
  ```text
  postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
  ```

* **Transaction Pooler (Port 6543)** — Ideal for serverless/high-concurrency application backends:
  ```text
  postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
  ```

> [!NOTE]
> If your database password contains special characters (e.g. `@`, `#`, `!`, `/`), ensure the password component of the URI is URL-encoded (e.g. `@` becomes `%40`).

---

## 3. Environment Variable Configuration

### Standalone Backend (`backend/.env`)

Copy `backend/.env.example` to `backend/.env` and update the database settings:

```env
# Application Settings
APP_ENV=development
DEBUG=false

# Canonical Database URL (Points to Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Supabase Credentials (Backend Server Scope Only)
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### Docker Compose Infrastructure (`.env`)

For Docker deployment, copy `.env.example` to `.env` in the repository root:

```env
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

---

## 4. Database Migrations (Alembic)

All AGENTPAY database structures (Users, Roles, Permissions, Agents, Agent Identity, Policies, Policy Rules, Risk Decisions, Fraud Predictions, XAI Explanations, Purchase Requests, Transactions, Audit Logs, Security Events) are managed via Alembic.

### Running Migrations Against Supabase

```powershell
# Windows PowerShell
cd backend/apps/agent-runtime
$env:DATABASE_URL="postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
d:\PROJECT\ANGENT-PAY\backend\.venv\Scripts\python.exe -m alembic upgrade head
```

```bash
# Linux / macOS / Bash
cd backend/apps/agent-runtime
export DATABASE_URL="postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
alembic upgrade head
```

### Migration Verification Commands

Confirm current migration state and history:

```bash
# Check current migration revision applied to database
alembic current

# Check target head revision defined in codebase
alembic heads

# View complete migration history sequence
alembic history
```

---

## 5. Local PostgreSQL vs. Supabase Switching

To switch between local Docker PostgreSQL and cloud Supabase PostgreSQL, simply change the `DATABASE_URL` environment variable:

* **Local Docker PostgreSQL**:
  ```env
  DATABASE_URL=postgresql://postgres:postgres_dev_pass@localhost:5432/agentpay_dev
  ```

* **Supabase Cloud PostgreSQL**:
  ```env
  DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
  ```

No code modifications are necessary. FastAPI automatically parses and normalizes the connection URL.

---

## 6. Health & Readiness Verification

### Process Liveness Probe
```http
GET /api/v1/health
```
- **Response**: `{"success": true, "data": {"status": "healthy"}, "meta": {...}}`
- Verifies FastAPI application process responsiveness.

### Traffic Readiness Probe
```http
GET /api/v1/ready
```
- **Response**: `{"success": true, "data": {"status": "ready"}, "meta": {...}}`
- Evaluates database connectivity (`SELECT 1`) and system operational readiness.

---

## 7. Troubleshooting & Best Practices

1. **Connection Timeout / Disconnection**:
   - Ensure `db_pool_pre_ping=True` (configured by default in `Settings`).
   - For Supabase Transaction Pooler (port 6543), ensure prepared statement pooling is compatible with your session manager.

2. **Special Characters in Passwords**:
   - If password is `P@ssword!`, format connection string as `postgresql://postgres.[REF]:P%40ssword%21@host:5432/postgres`.

3. **Git Security Audit**:
   - Ensure `.env` and `.env.local` remain in `.gitignore`.
   - Never commit raw passwords or `SUPABASE_SERVICE_ROLE_KEY` to source control.
