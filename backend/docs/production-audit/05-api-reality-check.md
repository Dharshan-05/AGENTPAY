# 05 — API Reality Check & Data Layer Classification

## 1. Classification Methodology
* **TYPE A**: Real Backend API Integration (`apps/api` Express Backend + PostgreSQL Database)
* **TYPE B**: Frontend Mock Service with static state array
* **TYPE C**: Typed Zod Contract Mock matching `@agentpay/api-contracts`
* **TYPE D**: Fake API abstraction

## 2. API Endpoint Classification Table

| API Target Endpoint | Frontend Data File | Type Classification | Contract Matched | Production Readiness |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/analytics/overview` | `mock/agentPay/analytics.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/payments` | `mock/agentPay/payments.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/payments/{id}` | `mock/agentPay/payments.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/agents` | `mock/agentPay/agents.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/agents/{id}` | `mock/agentPay/agents.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/settlements` | `mock/agentPay/settlements.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/reconciliation/discrepancies`| `mock/agentPay/settlements.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/risk/dashboard` | `mock/agentPay/risk.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |
| `GET /api/v1/risk/assessments/{id}` | `mock/agentPay/risk.ts` | **TYPE C (Zod Contract Mock)** | `@agentpay/api-contracts` | **MOCK ADAPTER READY** |

---

## 3. Findings
* The frontend consumes TYPE C Zod contract mock datasets (`apps/web/src/mock/agentPay/`).
* The backend API server (`apps/api/src/index.ts`) is established in the monorepo, ready for full HTTP wiring in future phase.
