# AGENTPAY — 31: Multi-Tier Authorization Middleware Foundation

## 1. Middleware Execution Order

```
[ Request ] ──> 1. Auth Middleware (JWT/HMAC Verification)
            ──> 2. Tenant Context Middleware (SET LOCAL app.current_tenant)
            ──> 3. RBAC & Scope Middleware (Capability Check)
            ──> 4. Controller Router
```
