# AGENTPAY — Information Architecture & User Experience Blueprint

## 1. Primary Navigation Hierarchy

```
AGENTPAY ENTERPRISE OPERATIONS PLATFORM
│
├── 📊 Overview (/agent-pay)
│   ├── Total Transaction Volume & Success Rate
│   ├── Agent Fleet Health & Active Autonomous Intents
│   ├── Settlement Pipeline Summary
│   └── Real-time AGENTGUARD Security Alerts
│
├── 💳 Payments (/payments)
│   ├── Transactions (/payments/transactions)
│   ├── Transaction Detail View (/payments/transactions/[id])
│   └── Refunds & Exceptions (/payments/refunds)
│
├── 🤖 Agent Fleet (/agents)
│   ├── All Autonomous Agents (/agents)
│   └── Agent Performance & Capabilities (/agents/[id])
│
├── 🏪 Merchants (/merchants)
│   ├── Merchant Overview & Accounts (/merchants)
│   └── Merchant-Agent Capability Rules (/merchants/[id])
│
├── 🏦 Settlements (/settlements)
│   ├── Settlement Batches (/settlements)
│   └── Ledger Reconciliation Engine (/settlements/reconciliation)
│
├── 🛡️ Risk & FraudGuard (/risk)
│   ├── Risk & Threat Overview (/risk)
│   └── Investigation Workbench (/risk/investigations/[id])
│
├── 📈 Analytics (/analytics)
│   └── Financial Performance & Latency Metrics
│
└── 🧠 AI Intelligence (/ai-insights)
    ├── Anomaly Detection Signals
    └── Policy Optimization Recommendations
```

---

## 2. Layout Hierarchy & Slot Architecture

```
+-----------------------------------------------------------------------------------+
| SIDEBAR NAVIGATION           | TOP HEADER NAVBAR                                 |
| - Logo & Tenant Switcher     | - Global Search (Cmd+K) | Notifications | Profile |
| - Primary Nav Links          +---------------------------------------------------+
|   * Overview                 | BREADCRUMBS: Home / Payments / Transactions / #102 |
|   * Payments                 +---------------------------------------------------+
|   * Agent Fleet              | PAGE TITLE & ACTION BUTTONS                       |
|   * Merchants                | "Transaction pay_K123456789" [Refund] [Download]  |
|   * Settlements              +---------------------------------------------------+
|   * Risk & FraudGuard        | KPI SUMMARY CARDS GRID (4 Columns)                |
|   * Analytics                +---------------------------------------------------+
|   * AI Intelligence          | FILTER & SEARCH TOOLBAR                           |
| - System Health Indicator    +---------------------------------------------------+
| - Theme / Collapse Toggle    | MAIN DATA TABLE / WORKBENCH CARD                  |
|                              | [ Checkbox | ID | Agent | Amount | Status | Action ]|
|                              +---------------------------------------------------+
|                              | PAGINATION FOOTER (Showing 1-20 of 1,420 items)   |
+-----------------------------------------------------------------------------------+
```

---

## 3. Interaction & Modal Control Flow

1. **Transaction Lifecycle Deep-Dive**: Clicking any row in `DataTable` navigates to `/payments/transactions/[id]`, displaying complete execution traces, signature verification hashes, and double-entry ledger postings.
2. **Human Approval Escalation**: High-risk transactions requiring manual escalation open an accessible `ApprovalModal` featuring SHAP feature attribution weights and explicit Approve / Reject controls.
3. **Emergency Agent Suspension**: Clicking `Suspend Agent` triggers a high-priority confirmation dialog that instantly revokes the agent's capability tokens.
