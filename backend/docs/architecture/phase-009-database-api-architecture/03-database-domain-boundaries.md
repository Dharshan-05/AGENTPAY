# AGENTPAY — 03: Logical Database Domain Boundaries & Table Ownership

## 1. 19 Logical Database Domains

| Domain | Primary Tables | Component Owner |
| :--- | :--- | :--- |
| **IDENTITY** | `users`, `roles`, `permissions`, `user_roles` | Identity Service |
| **TENANCY** | `tenants`, `tenant_settings`, `tenant_memberships` | Tenant Service |
| **AGENTS** | `agents`, `agent_identities`, `agent_capabilities` | Agent Service |
| **MERCHANTS** | `merchants`, `merchant_accounts`, `merchant_risk` | Merchant Service |
| **CATALOG** | `products`, `catalog_items` | Catalog Service |
| **ORDERS** | `orders`, `order_items` | Order Service |
| **PAYMENTS** | `payment_intents`, `payment_authorizations`, `payments`, `payment_attempts` | Payment Orchestrator |
| **REFUNDS** | `refunds`, `refund_attempts` | Refund Service |
| **RISK** | `risk_assessments`, `risk_decisions` | FRAUDGUARD Service |
| **TRUST** | `trust_assessments`, `trust_scores` | Trust Intelligence Service |
| **POLICY** | `policies`, `policy_versions`, `policy_rules` | Policy Engine |
| **APPROVALS** | `approval_requests` | Approval Center |
| **LEDGER** | `ledger_accounts`, `ledger_transactions`, `ledger_entries` | Accounting Ledger Service |
| **RECONCILIATION**| `reconciliation_records`, `reconciliation_items` | Reconciliation Worker |
| **WEBHOOKS** | `webhook_events`, `webhook_attempts` | Webhook Listener |
| **EVENTS** | `outbox_events`, `event_deliveries` | Event Publisher Worker |
| **AUDIT** | `audit_events` | Security Audit Service |
| **NOTIFICATIONS**| `notifications` | Notification Worker |
| **ANALYTICS** | `analytics_aggregates` | Data Warehouse / Analytics |
