# AGENTGUARD Architecture Specification: Phase 185 — Policy Management

## Overview
Phase 185 establishes the AgentGuard Security Policy Management architecture, defining security and business constraints governing agent actions.

## ORM & Data Architecture
- **Model Reuse**: Reuses existing `SecurityPolicy` ORM entity in [`app/infrastructure/database/models/security_policy.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/security_policy.py). Zero duplicate models created.
- **Tenant Scope Isolation**: All queries filter by `tenant_id == current_user.tenant_id`. No cross-tenant reads, updates, or deletes.
- **Lifecycle States**:
  - `DRAFT`: Initial creation state.
  - `ACTIVE`: Enforced or monitored policy.
  - `INACTIVE`: Temporarily disabled policy.
  - `ARCHIVED`: Soft-deleted policy (`deleted_at is not None`).
- **Priority Model**: Integer priority (`priority >= 0`; default `100`). Higher priority numbers take precedence during policy evaluation and conflict resolution.
- **Extensible Policy Types**: `spending`, `transaction`, `category`, `merchant`, `time`, `behavior`, `composite`.

## Security & Privacy
- Fail-closed evaluation and access semantics.
- Non-existent or cross-tenant policy lookups return `404 Not Found`.
- Zero secret leakage in policy `configuration` JSONB.
