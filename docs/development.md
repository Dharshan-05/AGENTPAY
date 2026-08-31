# AGENTPAY — Local Development Guide

This document outlines options for running AGENTPAY locally during development.

---

## Option A: Full Docker Stack (Recommended)

Spins up Frontend, Backend, PostgreSQL, and Redis in isolated containers:

```bash
cp .env.example .env
docker compose up --build
```

Access Points:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Option B: Hybrid Development (Local Process + Local/Supabase DB)

Run PostgreSQL and Redis via Docker, and backend/frontend processes directly on host machine:

### 1. Start Database & Caching Services
```bash
docker compose up -d agentpay-postgres agentpay-redis
```

### 2. Run FastAPI Backend
```bash
cd backend/apps/agent-runtime
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Run Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```
