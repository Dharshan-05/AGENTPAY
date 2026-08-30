# 01 — Project Structure & Monorepo Architecture Audit

## 1. Monorepo Baseline Verification
* **Package Manager**: PNPM v9.1.0 (`pnpm-workspace.yaml`)
* **Task Orchestrator**: Turborepo v1.12.4 (`turbo.json`)
* **Frontend Framework**: Next.js 14 (App Router) + React 18 (`apps/web`)
* **Core API Gateway**: Express Node.js TypeScript (`apps/api`)
* **AI Runtime Service**: Python FastAPI + XGBoost (`apps/agent-runtime`)
* **AGENTGUARD Security Control Plane**: Express Node.js (`apps/agentguard`)
* **Background Outbox Worker**: Node.js Event Poller (`apps/worker`)
* **Shared Packages**: 12 packages in `packages/*` (`@agentpay/config`, `@agentpay/types`, `@agentpay/api-contracts`, `@agentpay/database`, `@agentpay/auth`, `@agentpay/security`, `@agentpay/payments`, `@agentpay/agent-core`, `@agentpay/agentguard-core`, `@agentpay/events`, `@agentpay/observability`, `@agentpay/test-utils`)

---

## 2. Directory Hierarchy Audit

```text
d:\PROJECT\ANGENT PAY\
├── apps/
│   ├── web/               # Next.js 14 App Router UI
│   ├── api/               # Express Core Gateway API
│   ├── agent-runtime/     # Python FastAPI AI Engine
│   ├── agentguard/        # Security Control Plane
│   └── worker/            # Outbox Worker
├── packages/              # 12 Shared TypeScript Monorepo Packages
├── docs/                  # Architecture & Phase Specifications
├── docker-compose.yml     # Local PostgreSQL & Redis stack
├── package.json           # Monorepo root manifest
└── tsconfig.base.json     # Master TypeScript compiler settings
```
