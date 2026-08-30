# 02 — Existing Pages & Visual Baseline Inventory

## 1. Inventory Table of Completed Stitch & Agent Pay Pages

| Page Name | Route | Module ID | Primary Purpose | Key Components | API / Mock Dataset | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Root Redirect** | `/` | Core | Redirect to `/agent-pay` | Next `redirect()` | N/A | **ACTIVE** |
| **Executive Overview** | `/agent-pay` | Module 01 | Executive KPI summary & volume | `StatCard`, `DataTable` | `analytics.ts`, `payments.ts` | **ACTIVE** |
| **Payment Transactions** | `/payments/transactions` | Module 02 | Filterable payment execution log | `DataTable`, `FilterToolbar` | `payments.ts` | **ACTIVE** |
| **Transaction Detail** | `/payments/transactions/[id]` | Module 02 | Proof of Authority & ledger trace | `PageHeader`, `RiskScore` | `payments.ts` | **ACTIVE** |
| **Agent Fleet Manager** | `/agents` | Module 03 | Autonomous agent fleet manager | `AgentCard`, `StatusBadge` | `agents.ts` | **ACTIVE** |
| **Agent Profile & Trust** | `/agents/[id]` | Module 03 | Agent capabilities & kill switch | `TrustGauge`, `CapabilityList`| `agents.ts` | **ACTIVE** |
| **Merchant Operations** | `/merchants` | Module 04/05 | Merchant partners & MID config | `MerchantCard`, `KYCBadge` | Merchant Mock | **ACTIVE** |
