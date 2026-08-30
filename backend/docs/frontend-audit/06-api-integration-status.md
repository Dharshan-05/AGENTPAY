# 06 — API Integration Status & Data Binding Matrix

All frontend pages consume strongly-typed mock data adapters in `apps/web/src/mock/agentPay/` matching the `@agentpay/api-contracts` schemas.

* `GET /api/v1/analytics/overview` $\rightarrow$ `MOCK_OVERVIEW_ANALYTICS`
* `GET /api/v1/payments` $\rightarrow$ `MOCK_PAYMENT_TRANSACTIONS`
* `GET /api/v1/agents` $\rightarrow$ `MOCK_AGENTS`
* `GET /api/v1/settlements` $\rightarrow$ `MOCK_SETTLEMENTS`
* `GET /api/v1/risk/dashboard` $\rightarrow$ `MOCK_RISK_ALERTS`
