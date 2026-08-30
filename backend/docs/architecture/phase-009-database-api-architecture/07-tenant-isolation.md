# AGENTPAY — 07: PostgreSQL Row-Level Security (RLS) Policy Specifications

## 1. Row-Level Security Policy Engine

PostgreSQL Row-Level Security (RLS) is enabled on 100% of tenant-scoped tables:

```sql
-- Enable RLS on Payments table
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Create Tenant Isolation Policy
CREATE POLICY tenant_isolation_policy ON payments
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
```

---

## 2. RLS Execution Preconditions

1. **Trusted Context**: API middleware executes `SET LOCAL app.current_tenant = 'tenant_xyz'` upon authenticating JWT requests.
2. **Superuser Bypass Prevention**: Application database connection pool uses a restricted non-superuser role (`agentpay_app`).
