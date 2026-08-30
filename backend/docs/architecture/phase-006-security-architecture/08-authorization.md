# AGENTPAY — 08: RBAC + ABAC Scoped Capability Authorization Model

## 1. Hybrid RBAC + ABAC Model

AGENTPAY combines Role-Based Access Control (RBAC) for coarse role assignment with Attribute-Based Access Control (ABAC) and Capability Scopes for dynamic context enforcement.

```
+-----------------------------------------------------------------------+
|                       AUTHORIZATION DECISION ENGINE                   |
+-----------------------------------------------------------------------+
|  Role (RBAC)        : Is actor USER, AGENT, MERCHANT, or ADMIN?       |
|  Capability (Scope) : Does agent hold 'spend:intent_create' scope?     |
|  Tenant Context     : Does resource tenant_id match actor tenant_id?  |
|  Policy Rules (ABAC): Does amount <= single_limit & MCC != blocked?   |
|  Risk Score (ABAC)  : Is risk_score <= max_allowed_risk_threshold?    |
+-----------------------------------------------------------------------+
```

---

## 2. Agent Capability Scopes

* `product.search`: Search merchant product catalogs (Read-only).
* `cart.create`: Assemble item shopping cart.
* `spend:intent_create`: Initiate payment intent request payload.
* `status:query`: Query intent status and execution receipt.
* `intent:cancel`: Cancel pending intent request.

*Payment Execution Privilege*: `spend:intent_create` must be explicitly granted by the human owner.
