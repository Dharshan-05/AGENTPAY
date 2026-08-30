# AGENTPAY — 06: Identity Principals, GUIDs & Key Governance

## 1. Identity Principals Taxonomy

AGENTPAY treats human owners, AI agents, merchants, system services, and background workers as distinct, independently verifiable security principals.

```mermaid
graph TD
    subgraph Identity Principals
        U[Human Owner: user_id]
        A[AI Agent: agent_id]
        M[Merchant: merchant_id]
        T[Tenant: tenant_id]
        S[System Service: service_id]
    end

    U -->|Owns & Authorizes| A
    U -->|Belongs to| T
    A -->|Initiates Intents for| T
    M -->|Receives Payments from| T
```

---

## 2. Mandatory Identification Keys

* `tenant_id`: Unique organization/user workspace GUID (`tenant_7f8a...`).
* `user_id`: Unique human account owner GUID (`usr_91a0...`).
* `agent_id`: Unique AI agent principal GUID (`agt_8f9b...`).
* `merchant_id`: Unique merchant identification GUID (`mch_1234...`).
* `transaction_id`: Unique payment intent GUID (`intent_7f8a...`).
* `decision_id`: Unique AGENTGUARD authorization decision GUID (`dec_9f8a...`).
