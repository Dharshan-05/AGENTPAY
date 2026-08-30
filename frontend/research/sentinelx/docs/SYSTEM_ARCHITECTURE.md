# SentinelX — System Architecture

## High-level topology

```
┌─────────────────┐        ┌──────────────────────────────┐
│  Next.js (web)   │  HTTP  │  Fastify (API) :3001          │
│  App Router      │───────▶│                               │
│  :3000           │        │  ┌─────────────────────────┐  │
└─────────────────┘        │  │  8-Agent Pipeline        │  │
        │                  │  │  Inspector → Detection    │  │
        │ Socket.IO        │  │  → Policy → Risk → Rewrite│  │
        │ (agent:update)   │  │  → LLM → Audit → Memory   │  │
        └─────────────────▶│  └─────────────────────────┘  │
                           │           │                    │
                           │  ┌────────▼──────────┐         │
                           │  │ Store (mem/Prisma) │         │
                           │  │ audit · policies   │         │
                           │  │ rules · alerts     │         │
                           │  └───────────────────┘         │
                           └──────────────────────────────┘
```

## Backend (`apps/api`)

- **`server.ts`** — Fastify bootstrap, CORS, rate limiting, Socket.IO server, route registration, copilot engine, health + scan endpoints.
- **`routes/enterprise.ts`** — `/executive`, `/soc`, `/twin`, `/analytics`, `/system` telemetry endpoints.
- **`agents/`** — one module per agent. Each agent exposes `run()` + `toTrace()` producing a standard `AgentTraceEntry` (status, confidence, execution time).
- **`lib/store.ts`** — data-access facade over Prisma (PostgreSQL) with a fully-featured in-memory fallback so the demo runs without external services.
- **`lib/redis.ts`** — seeds demo data when the database is empty.
- **`lib/prisma.ts`** — PostgreSQL client with availability detection.

## Frontend (`apps/web`)

- **`app/(dashboard)/*`** — 19 product pages, all client components, all animated, all with skeleton loading and empty states.
- **`components/ui/*`** — shared primitives: badges, gauges, toasts, confetti, world map, explainable-AI panel, magnetic buttons.
- **`components/layout/*`** — sidebar, header, status bar (live-polling system telemetry), command palette.
- **`lib/api.ts`** — typed API client + severity/decision color maps.
- **`lib/live.ts`** — Socket.IO subscription for live agent updates during scans.

## Data flow — a prompt scan

1. Web POSTs `/api/scan`.
2. Pipeline runs agents sequentially, emitting `agent:update` over Socket.IO as each completes.
3. Web animates the pipeline live (progress, latency, confidence per agent).
4. Pipeline commits an audit record and returns the full result + trace.
5. Result renders with explainable-AI, and the web offers replay/export.

## Design decisions

- **Rule-based intelligence** — deterministic, reproducible demo outputs. No external LLM dependency at runtime (LLM Adapter is a simulated gateway with provider routing).
- **In-memory demo mode** — `PostgreSQL` optional; store falls back to memory automatically, seeded with realistic data.
- **Explainability first** — every decision can be traced to a rule, a policy, a confidence value, and an alternative outcome.
