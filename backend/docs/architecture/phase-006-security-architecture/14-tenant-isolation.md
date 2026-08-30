# AGENTPAY — 14: Multi-Tenant Data Isolation & PostgreSQL RLS

## 1. PostgreSQL Row-Level Security (RLS) Policies

All multi-tenant database tables enforce PostgreSQL Row-Level Security (RLS).

```sql
-- Enable RLS on payment_intents table
ALTER TABLE payment_intents ENABLE ROW LEVEL SECURITY;

-- Create Tenant Isolation Policy
CREATE POLICY tenant_isolation_policy ON payment_intents
    USING (tenant_id = current_setting('app.current_tenant'))
    WITH CHECK (tenant_id = current_setting('app.current_tenant'));
```

---

## 2. Redis Key Namespacing

Redis edge keys enforce strict namespace prefixes: `tenant:<tenant_id>:agent:<agent_id>:<key_name>`, rendering cross-tenant key access impossible by design.
