# ATIM Phase 19 Architecture — Enterprise API Security & Authorization Hardening

## Executive Summary
**ATIM Phase 19** implements a centralized authorization boundary and API security hardening layer for **AgentPay Transaction Intelligence Model (ATIM)** infrastructure.

Phase 19 features:
1. **Centralized Authorization Service (`ATIMAuthorizationService`)**: Evaluates principal authentication, tenant ownership (`authenticated_tenant == target_tenant`), agent ownership, and fine-grained RBAC permissions prior to executing any downstream operations.
2. **Fine-Grained RBAC Permission Matrix**:
   - `ATIM_POLICY_READ`
   - `ATIM_POLICY_CREATE`
   - `ATIM_POLICY_SUBMIT`
   - `ATIM_POLICY_APPROVE`
   - `ATIM_POLICY_ACTIVATE`
   - `ATIM_POLICY_SUSPEND`
   - `ATIM_POLICY_RETIRE`
   - `ATIM_POLICY_AUDIT`
   - `ATIM_SYSTEM_ADMIN`
3. **Pre-Execution Authorization Boundary**: Evaluates rate limits, cost quotas, tenant scoping, and RBAC permissions BEFORE invoking expensive LLM inference, database queries, or model routing.
4. **IDOR & Cross-Tenant Defense**: Enforces server-resolved tenant context (`current_user.tenant_id`). Client-supplied or LLM-generated tenant IDs are explicitly ignored.

---

## Authorization Boundary Data Flow

```text
HTTP REQUEST
     │
     ▼
AUTHENTICATION (JWT Principal Verification)
     │
     ▼
SERVER TENANT IDENTITY RESOLUTION (current_user.tenant_id)
     │
     ▼
ATIM AUTHORIZATION SERVICE (ATIMAuthorizationService)
 ├── Tenant Scope Check (authenticated_tenant == target_tenant)
 ├── Agent Scope Check (agent_id ownership)
 └── RBAC Permission Check (SecurityPermission match)
     │
     ├────────────► Denied: HTTP 403 Forbidden / Fail Closed
     ▼
RATE LIMIT & QUOTA EVALUATION
     │
     ▼
ATIM RUNTIME EXECUTION
```
