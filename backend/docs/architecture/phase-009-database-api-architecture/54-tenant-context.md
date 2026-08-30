# AGENTPAY — 54: Trusted Server-Side Tenant Context Resolution

## 1. Tenant Context Resolution Rules

* **Client `tenant_id` Untrusted**: API controllers never trust `tenant_id` claims passed in request query parameters or JSON body fields.
* **Server-Side Extraction**: `tenant_id` is extracted strictly from the cryptographically verified JWT token payload or HMAC agent identity context during authentication.
* **Database Session Binding**: Extracted `tenant_id` is bound to the PostgreSQL session variable (`SET LOCAL app.current_tenant`).
