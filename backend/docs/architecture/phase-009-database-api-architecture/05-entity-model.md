# AGENTPAY — 05: Complete Relational Entity Model & Schema Inter-Relationships

## 1. Relational Entity Relationship Diagram

```mermaid
erDiagram
    TENANTS ||--o{ USERS : owns
    TENANTS ||--o{ AGENTS : provisions
    TENANTS ||--o{ MERCHANTS : registers
    TENANTS ||--o{ ORDERS : scope
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ PAYMENT_INTENTS : triggers
    PAYMENT_INTENTS ||--o| PAYMENT_AUTHORIZATIONS : receives
    PAYMENT_AUTHORIZATIONS ||--o| PAYMENTS : executes
    PAYMENTS ||--o{ PAYMENT_ATTEMPTS : attempts
    PAYMENTS ||--o{ REFUNDS : refunds
    PAYMENTS ||--o{ LEDGER_TRANSACTIONS : posts
    LEDGER_TRANSACTIONS ||--o{ LEDGER_ENTRIES : contains
```

---

## 2. Inviolable Schema Principles

* **Cascading Tenant Scope**: Every single relational record links to a `tenant_id`.
* **Restricted Deletions**: Deletions are forbidden on financial tables (`ON DELETE RESTRICT`).
