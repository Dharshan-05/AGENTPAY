# ATIM Phase 19 — Enterprise API Security Policy

## 1. Non-Negotiable API Security Invariants
1. **PRE-EXECUTION AUTHORIZATION**: Authorization evaluation **MUST** take place before executing database operations, model routing, or LLM inference calls.
2. **SERVER-AUTHORITATIVE TENANT IDENTITY**: Tenant scope is strictly derived from the authenticated session context (`current_user.tenant_id`). Client payload tenant IDs or LLM-generated tenant IDs **MUST NEVER** override server identity.
3. **FINE-GRAINED RBAC**: Generic permissions (e.g. `admin`) are prohibited. Specific permissions (`ATIM_POLICY_READ`, `ATIM_POLICY_APPROVE`, `ATIM_SYSTEM_ADMIN`) must be enforced per API endpoint.
4. **FAIL CLOSED**: Invalid JWTs, expired credentials, RBAC mismatches, or cross-tenant access attempts immediately fail closed returning `HTTP 401 / 403`.
