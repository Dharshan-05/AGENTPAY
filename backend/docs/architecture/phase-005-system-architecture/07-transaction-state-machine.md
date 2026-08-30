# AGENTPAY — 07: 14-State Transaction State Machine Specification

## 1. State Machine Diagram

Every financial intent in AGENTPAY transitions through an atomic 14-state transaction lifecycle.

```mermaid
stateDiagram-v2
    [*] --> CREATED: Ingest Payment Intent Payload
    CREATED --> VALIDATING: Schema & Auth Check
    VALIDATING --> POLICIED: AGENTGUARD Policy Evaluation
    VALIDATING --> REJECTED: Schema/Auth Error
    POLICIED --> RISK_CHECK: FRAUDGUARD Risk Scoring
    POLICIED --> BLOCKED: Policy Boundary Breach

    RISK_CHECK --> AUTHORIZED: Decision == ALLOW (Under Ceiling)
    RISK_CHECK --> PENDING_APPROVAL: Decision == REVIEW (Exceeds Ceiling)
    RISK_CHECK --> BLOCKED: Decision == BLOCK (High Risk)

    PENDING_APPROVAL --> AUTHORIZED: Human Clicks "APPROVE"
    PENDING_APPROVAL --> REJECTED: Human Clicks "REJECT"
    PENDING_APPROVAL --> EXPIRED: 15-Minute TTL Elapsed

    AUTHORIZED --> PROCESSING: Payment Adapter Dispatch
    PROCESSING --> EXECUTED: Razorpay Settlement Confirmed
    PROCESSING --> FAILED: Gateway Error / Timeout (5s)

    EXECUTED --> RECONCILED: Webhook Signature Verified
    EXECUTED --> REFUND_PENDING: User/Merchant Initiates Refund
    REFUND_PENDING --> REFUNDED: Refund Processed

    REJECTED --> [*]
    BLOCKED --> [*]
    EXPIRED --> [*]
    FAILED --> [*]
    RECONCILED --> [*]
    REFUNDED --> [*]
```

---

## 2. Transition Rules & Preconditions

| State | Legal Target States | Required Condition | Atomic DB Operation |
| :--- | :--- | :--- | :--- |
| `CREATED` | `VALIDATING` | Schema validation succeeds | `UPDATE state = 'VALIDATING'` |
| `VALIDATING` | `POLICIED`, `REJECTED` | AGENTGUARD policy check complete | `UPDATE state = 'POLICIED'` |
| `POLICIED` | `RISK_CHECK`, `BLOCKED` | Feature extraction complete | `UPDATE state = 'RISK_CHECK'` |
| `RISK_CHECK` | `AUTHORIZED`, `PENDING_APPROVAL`, `BLOCKED` | Risk scoring complete | `UPDATE state = 'AUTHORIZED'` |
| `PENDING_APPROVAL`| `AUTHORIZED`, `REJECTED`, `EXPIRED` | User action / 15m timeout | Lock row `SELECT FOR UPDATE` |
| `AUTHORIZED` | `PROCESSING` | Payment service dispatch | Lock row `SELECT FOR UPDATE` |
| `PROCESSING` | `EXECUTED`, `FAILED` | Gateway settlement result | `UPDATE state = 'EXECUTED'` |
| `EXECUTED` | `RECONCILED`, `REFUND_PENDING` | Webhook signature verified | Append SHA-256 block hash |
