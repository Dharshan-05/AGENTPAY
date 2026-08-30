# AGENTPAY — 45: GitHub Actions CI/CD Pipeline Blueprint (`.github/workflows/ci.yml`)

## 1. CI Workflow Stages

```
[ Git Push / PR ]
       │
       ▼
[ Job 1: Lint & Format ] ──> pnpm lint && pnpm format:check
       │
       ▼
[ Job 2: Typecheck ]     ──> pnpm typecheck
       │
       ▼
[ Job 3: Security Scan ] ──> gitleaks && pnpm security:scan
       │
       ▼
[ Job 4: Integration ]   ──> Provision Postgres & Redis Services -> pnpm test:integration
       │
       ▼
[ Job 5: Monorepo Build] ──> pnpm build
```
