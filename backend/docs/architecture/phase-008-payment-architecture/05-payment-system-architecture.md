# AGENTPAY — 05: End-to-End Logical Payment Processing Architecture

## 1. System Processing Flow

```mermaid
graph TB
    CLIENT[Client / AI Agent] --> GW[API Gateway & Edge Auth]
    GW --> INTENT_SVC[Payment Intent Service]
    INTENT_SVC --> AGENTGUARD[AGENTGUARD Policy Engine]
    AGENTGUARD --> FRAUDGUARD[FRAUDGUARD 12-D ML Risk Engine]
    FRAUDGUARD --> AUTH_SVC[Payment Authorization Service]
    AUTH_SVC --> ORCHESTRATOR[Payment Orchestrator]
    ORCHESTRATOR --> ADAPTER[Razorpay Provider Adapter]
    ADAPTER --> RAZORPAY[Razorpay Payment Rails]
    RAZORPAY --> WEBHOOK[Webhook Listener Service]
    WEBHOOK --> STATE_ENGINE[18-State Payment Machine]
    STATE_ENGINE --> LEDGER[Double-Entry Accounting Ledger]
    LEDGER --> RECON[Reconciliation Engine]
    RECON --> AUDIT[Append-Only SHA-256 Audit Chain]
```

---

## 2. Execution Principles

1. **Deterministic Interception**: The AI agent proposes the intent; AGENTGUARD evaluates policy caps; FRAUDGUARD evaluates ML risk scores.
2. **Authorized Settlement**: Payment Orchestrator dispatches execution to Razorpay strictly upon receiving a valid, signed `PaymentAuthorizationContext`.
