# AGENTPAY — Docker Infrastructure Guide

This guide describes how to run the full **AGENTPAY** containerized stack using Docker and Docker Compose.

---

## 1. Quick Start with Docker Compose

Run the entire AGENTPAY stack (Frontend, Backend, PostgreSQL, Redis) with a single command:

```bash
# 1. Clone or navigate to repo root
cd AGENTPAY

# 2. Copy environment template
cp .env.example .env

# 3. Build and start containers in detached mode
docker compose up --build -d
```

---

## 2. Services Topology

| Container Service | Image | Exposed Port | Health Check Endpoint / Command | Description |
| :--- | :--- | :---: | :--- | :--- |
| **`agentpay-frontend`** | Node 20 Alpine (Next.js) | `3000` | `http://localhost:3000` | Next.js Control Plane UI |
| **`agentpay-backend`** | Python 3.11 Slim (FastAPI) | `8000` | `http://localhost:8000/api/v1/health` | FastAPI REST API Gateway |
| **`agentpay-postgres`** | Postgres 15 Alpine | `5432` | `pg_isready -U postgres -d agentpay_dev` | Local PostgreSQL DB |
| **`agentpay-redis`** | Redis 7 Alpine | `6379` | `redis-cli ping` | Caching & Signal Store |

---

## 3. Environment Configuration

The containers read configuration from `.env` at root. Key variables include:

```env
# Backend Connection to PostgreSQL Container
DATABASE_URL=postgresql://postgres:postgres_dev_pass@agentpay-postgres:5432/agentpay_dev

# Backend Connection to Redis Container
REDIS_URL=redis://agentpay-redis:6379/0

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 4. Operational Commands

### Checking Service Logs
```bash
# All logs
docker compose logs -f

# Backend logs only
docker compose logs -f agentpay-backend

# Frontend logs only
docker compose logs -f agentpay-frontend
```

### Running Alembic Database Migrations Inside Docker
```bash
docker compose exec agentpay-backend alembic upgrade head
```

### Stopping the Stack
```bash
# Stop containers keeping volume data
docker compose down

# Stop containers and remove volumes (fresh reset)
docker compose down -v
```
