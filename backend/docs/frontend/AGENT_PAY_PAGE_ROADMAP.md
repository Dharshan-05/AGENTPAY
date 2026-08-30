# AGENTPAY — Page Implementation Roadmap & Prioritization

## 1. Page Prioritization Matrix

| Page Name | Route | Purpose | Allowed Roles | Priority | Reusable Components Used | Backend API Endpoint |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Executive Overview** | `/agent-pay` | Master operational dashboard & KPI metrics | Admin, Owner | **P0 (MVP)** | `StatCard`, `MetricChart`, `ActivityFeed` | `GET /api/v1/analytics/overview` |
| **Payment Transactions** | `/payments/transactions` | Filterable, paginated transaction log | Admin, Owner, Support | **P0 (MVP)** | `DataTable`, `FilterToolbar`, `StatusBadge` | `GET /api/v1/payments` |
| **Transaction Detail** | `/payments/transactions/[id]` | Full audit trail, signature & ledger trace | Admin, Owner, Support | **P0 (MVP)** | `PageHeader`, `AuditTimeline`, `JSONViewer` | `GET /api/v1/payments/{id}` |
| **Agent Fleet Manager** | `/agents` | List active autonomous AI agents & autonomy | Admin, Owner | **P0 (MVP)** | `AgentCard`, `AutonomyLevelBadge` | `GET /api/v1/agents` |
| **Agent Detail View** | `/agents/[id]` | Capabilities, risk history & kill-switch | Admin, Owner | **P0 (MVP)** | `PageHeader`, `CapabilityList`, `TrustGauge` | `GET /api/v1/agents/{id}` |
| **Settlement Dashboard** | `/settlements` | Batch settlements & payout tracking | Admin, Accountant | **P0 (MVP)** | `StatCard`, `LedgerTable` | `GET /api/v1/settlements` |
| **Settlement Reconciliation**| `/settlements/reconciliation` | Discrepancy resolution workbench | Admin, Accountant | **P0 (MVP)** | `DiscrepancyCard`, `ActionModal` | `GET /api/v1/reconciliation/discrepancies` |
| **Risk & Threat Center** | `/risk` | FRAUDGUARD anomaly dashboard | Admin, SecOps | **P0 (MVP)** | `RiskScoreGauge`, `ThreatAlertList` | `GET /api/v1/risk/dashboard` |
| **Risk Investigation** | `/risk/investigations/[id]` | Deep SHAP feature attribution workbench | Admin, SecOps | **P0 (MVP)** | `SHAPChart`, `ApprovalCard` | `GET /api/v1/risk/assessments/{id}` |
| **Merchant Overview** | `/merchants` | Merchant partner relations & caps | Admin, Merchant | **P1** | `MerchantCard`, `KYCBadge` | `GET /api/v1/merchants` |
| **Refunds Management** | `/payments/refunds` | Initiate & track refund claims | Admin, Support | **P1** | `DataTable`, `RefundModal` | `GET /api/v1/refunds` |
| **Financial Analytics** | `/analytics` | Volume, latency & failure rate breakdown | Admin, Owner | **P1** | `MetricChart`, `ExportButton` | `GET /api/v1/analytics/financial` |
| **AI Intelligence Hub** | `/ai-insights` | AGENTGUARD anomaly signals & recommendations | Admin, SecOps | **P1** | `RecommendationCard`, `AnomalyFeed` | `GET /api/v1/agentguard/insights` |
