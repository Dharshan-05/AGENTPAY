# AGENTPAY — API Integration Matrix & Endpoint Contract

## 1. Frontend-to-Backend Integration Matrix

| Page Name | Target Endpoint | HTTP Method | Request Params / Body | Response Schema | Auth Guard | RBAC Scope | Backend Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Overview** | `/api/v1/analytics/overview` | `GET` | `tenant_id` | `OverviewAnalytics` | Bearer JWT | `read:analytics` | **READY** |
| **Transactions** | `/api/v1/payments` | `GET` | `page, limit, status, q` | `PaginatedPayments` | Bearer JWT | `read:payments` | **READY** |
| **Transaction Detail** | `/api/v1/payments/{id}` | `GET` | `payment_id` | `PaymentDetailRecord` | Bearer JWT | `read:payments` | **READY** |
| **Agent Fleet** | `/api/v1/agents` | `GET` | `tenant_id, status` | `AgentListResponse` | Bearer JWT | `read:agents` | **READY** |
| **Agent Detail** | `/api/v1/agents/{id}` | `GET` | `agent_id` | `AgentProfileRecord` | Bearer JWT | `read:agents` | **READY** |
| **Settlements** | `/api/v1/settlements` | `GET` | `tenant_id, status` | `SettlementBatches` | Bearer JWT | `read:settlements` | **READY** |
| **Reconciliation** | `/api/v1/reconciliation/discrepancies` | `GET` | `settlement_id` | `DiscrepancyList` | Bearer JWT | `write:ledger` | **READY** |
| **Risk Dashboard** | `/api/v1/risk/dashboard` | `GET` | `tenant_id` | `RiskMetrics` | Bearer JWT | `read:risk` | **READY** |
| **Risk Investigation**| `/api/v1/risk/assessments/{id}` | `GET` | `alert_id` | `RiskAssessmentXAI` | Bearer JWT | `write:risk_override` | **READY** |
| **Merchant Operations**| `/api/v1/merchants` | `GET` | `tenant_id` | `MerchantListResponse` | Bearer JWT | `read:merchants` | **READY** |
| **Refunds** | `/api/v1/refunds` | `GET` | `payment_id` | `RefundListResponse` | Bearer JWT | `write:refunds` | **READY** |
| **Analytics** | `/api/v1/analytics/financial` | `GET` | `range=7d` | `FinancialAnalytics` | Bearer JWT | `read:analytics` | **READY** |
| **AI Intelligence** | `/api/v1/agentguard/insights` | `GET` | `tenant_id` | `AIInsightSignals` | Bearer JWT | `read:agentguard` | **READY** |

---

## 2. Mock-to-Production Swap Architecture

All mock datasets in `apps/web/src/mock/agentPay/` implement the exact Zod contract interfaces defined in `@agentpay/api-contracts`. 
Replacing mock data with live TanStack Query API calls requires zero UI refactoring.
