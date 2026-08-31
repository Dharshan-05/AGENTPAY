# AGENTPAY — Zero-Trust Autonomous Agentic Commerce & Governance Platform

AGENTPAY is a production-grade infrastructure platform for secure autonomous agentic commerce, zero-trust payment intent governance, cryptographic identity verification, **AGENTGUARD** policy enforcement, and **FRAUDGUARD** real-time machine learning risk intelligence.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Browser Client                                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (HTTP / REST)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Next.js Frontend Control Plane (:3000)                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (HTTP / REST)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Gateway Service (:8000)                    │
│   • JWT Auth & RBAC Permissions        • Agent Management & Identity        │
│   • AGENTGUARD HITL Policy Engine      • FRAUDGUARD Real-Time ML Inference  │
│   • Purchase Request Orchestration     • Razorpay Webhook Boundary          │
└──────────────────┬───────────────────┬───────────────────┬──────────────────┘
                   │                   │                   │
                   ▼                   ▼                   ▼
         Local / Supabase DB       Redis Cache          Alembic
           (PostgreSQL)           (:6379 Caching)     Migrations
```

---

## Infrastructure & Deployment

### Quick Start with Docker Compose

Run the entire AGENTPAY production stack (Frontend, Backend, PostgreSQL, Redis) with a single command:

```bash
# 1. Copy root environment template
cp .env.example .env

# 2. Build and launch Docker services
docker compose up --build -d
```

Service endpoints:
- **Frontend Control Plane**: `http://localhost:3000`
- **Backend API Gateway**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **ReDoc API Documentation**: `http://localhost:8000/redoc`

---

## Documentation

Detailed documentation guides are available in `/docs`:
- [Docker Infrastructure Guide](docs/docker.md) — Containerization setup, multi-stage builds, logs, and compose lifecycle.
- [Supabase Integration Guide](docs/supabase.md) — Managed cloud PostgreSQL configuration and Alembic migration runner setup.
- [Local Development Guide](docs/development.md) — Hybrid local development options and environment switching.

---

## Security Guarantees
- **Zero-Trust Token Governance**: Strict JWT authentication with refresh token rotation.
- **Backend-Only Service Keys**: Supabase service-role keys and database credentials are strictly isolated to the server.
- **Cryptographic Audit Hash**: Immutable chained transaction decision audit event logs.
