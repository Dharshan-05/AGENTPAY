# 07 — Zod Contract Verification & Schema Parity

## 1. Schema Validation Audit
* Shared package `@agentpay/api-contracts` defines Zod validation schemas for requests and responses.
* All mock objects in `apps/web/src/mock/agentPay/` implement contract interfaces.
* Financial minor unit amounts (`amount: z.number().int().positive()`) are strictly validated against integer minor units (paisa). Zero floating point drift detected.
