# AGENTPAY — 03: Payment Domain Model Entities & Tenant Ownership

## 1. Domain Entities Architecture

```mermaid
erDiagram
    TENANT ||--o{ USER : owns
    TENANT ||--o{ AGENT : owns
    TENANT ||--o{ MERCHANT : manages
    TENANT ||--o{ ORDER : scope
    ORDER ||--o{ ORDER_ITEM : contains
    ORDER ||--o{ PAYMENT_INTENT : triggers
    PAYMENT_INTENT ||--o| PAYMENT_AUTHORIZATION : receives
    PAYMENT_AUTHORIZATION ||--o| PAYMENT : executes
    PAYMENT ||--o{ PAYMENT_ATTEMPT : attempts
    PAYMENT ||--o{ REFUND : refunds
    PAYMENT ||--o{ RECONCILIATION_RECORD : reconciles
    PAYMENT ||--o{ LEDGER_ENTRY : posts
```

---

## 2. Mandatory Domain Entities

* **`Tenant`**: Multi-tenant workspace principal (`tenant_id`).
* **`User`**: Account owner GUID (`user_id`).
* **`Agent`**: Autonomous agent GUID (`agent_id`).
* **`Merchant`**: Payee merchant GUID (`merchant_id`).
* **`Order`**: Order header (`order_id`) containing purchased items.
* **`PaymentIntent`**: Proposed financial transaction payload (`payment_intent_id`).
* **`PaymentAuthorization`**: Signed short-lived authorization token (`authorization_id`).
* **`Payment`**: Core settlement record (`payment_id`).
* **`PaymentAttempt`**: Individual provider settlement attempt (`attempt_id`).
* **`Refund`**: Refund request header (`refund_id`).
* **`ReconciliationRecord`**: Settlement discrepancy reconciliation (`reconciliation_id`).
* **`LedgerEntry`**: Double-entry financial journal line (`ledger_entry_id`).
