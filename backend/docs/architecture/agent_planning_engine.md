# Phase 146 — Agent Planning Engine Architecture

## Purpose
Phase 146 introduces the Agent Planning Engine (`AgentPlanningService`) for AGENTPAY, orchestrating the pipeline from structured intent to validated plan representation.

## Architecture
```
Structured Intent
      ↓
Intent Validation
      ↓
Intent Normalization
      ↓
PLAN GENERATION (Phase 147)
      ↓
PLAN VALIDATION (Phase 148)
      ↓
Validated Plan Representation (Reusing PurchasePlan model)
```

## Key Invariants & Boundary Protection
- **Pure Representation Layer**: The planning engine ONLY generates and validates plan representations.
- **ZERO Execution**: MUST NOT call tools, execute payments, charge money, captured funds, or initiate payment provider sessions.
- **Server-Controlled Fields**: `tenant_id`, `agent_id`, `plan_id`, `created_at`, `status` are strictly server-controlled and rejected from client requests (`extra="forbid"`).
- **Tenant Isolation & IDOR Defense**: All operations check authenticated tenant scope (`AgentNotFoundError` 404).
