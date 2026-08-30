# AGENTPAY — 53: Multi-Tier Authorization (RBAC + ABAC + Agent Scopes)

## 1. Authorization Evaluation Layers

```
[ Ingress Request ] ──> Layer 1: RBAC Role Check (User / Admin Role)
                           │
                    ──> Layer 2: Agent Capability Scope Check ('spend:intent_create')
                           │
                    ──> Layer 3: ABAC Context Check (Single Limit, Budget, MCC)
```

Requests lacking explicit capability scopes or failing ABAC contextual checks are rejected immediately with HTTP 403 Forbidden.
