# AGENTPAY — 06: Agent Lifecycle State Machine

## 1. Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> CREATED: User Enrolls Agent Principal
    CREATED --> CONFIGURED: Assign Scopes & Budget Caps
    CONFIGURED --> VERIFIED: HMAC Secret Keys Provisioned
    VERIFIED --> ACTIVE: Agent Ready for Task Execution
    ACTIVE --> SUSPENDED: Anomaly Flagged / Emergency Stop
    ACTIVE --> REVOKED: Human User Revokes Agent Key
    SUSPENDED --> ACTIVE: Owner Verification Complete
    SUSPENDED --> REVOKED: Security Incident Confirmed
    REVOKED --> [*]: Sub-10ms Purge Complete
```

---

## 2. State Transition Controls

* `CREATED` $\rightarrow$ `CONFIGURED`: Requires human user assignment of capability scopes (`spend:intent_create`) and daily budget caps.
* `ACTIVE` $\rightarrow$ `SUSPENDED`: Triggered automatically by AGENTGUARD on velocity breach ($> 5\text{ req/s}$) or high risk score ($> 90$).
* `ACTIVE` $\rightarrow$ `REVOKED`: Evicts Redis edge authentication keys in $< 10\text{ ms}$.
