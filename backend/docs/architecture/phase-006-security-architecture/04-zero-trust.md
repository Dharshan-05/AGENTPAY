# AGENTPAY — 04: Zero-Trust Architecture & Continuous Verification

## 1. Zero-Trust Architecture Blueprint

```mermaid
graph TD
    REQ[Incoming API Request] --> ID[1. Identity Check]
    ID --> AUTH[2. Authentication Validation]
    AUTH --> TENANT[3. Tenant Context Injection]
    TENANT --> CAP[4. Capability Scope Authorization]
    CAP --> POLICY[5. AGENTGUARD Policy Gate]
    POLICY --> RISK[6. FRAUDGUARD Risk Scoring]
    RISK --> DECISION{7. Authorization Decision}
    DECISION -- ALLOW --> EXEC[8. Payment Execution]
    DECISION -- REVIEW --> ESCALATE[Escalate to Human Approval]
    DECISION -- BLOCK --> REJECT[Block & Log Alert]
    EXEC & ESCALATE & REJECT --> AUDIT[9. Immutable Audit Logging]
```

---

## 2. Server-Side Context Verification

Every request must establish: **WHO** (User/Agent GUID), **WHAT** (Action/Scope), **WHY** (Task Intent Context), **WHERE** (IP/Geo), **WHEN** (Timestamp Window), **FOR WHICH TENANT** (`tenant_id`), **WITH WHAT RISK** (`risk_score`). Authorization decisions are rendered 100% server-side.
