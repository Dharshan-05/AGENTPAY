# AGENTPAY — 56: PostgreSQL RLS Multi-Tenant Data Isolation

## 1. Data Isolation Controls

All payment database tables (`payment_intents`, `payments`, `refunds`, `ledger_entries`) enforce PostgreSQL Row-Level Security:

```sql
CREATE POLICY payment_tenant_isolation ON payments
    USING (tenant_id = current_setting('app.current_tenant'))
    WITH CHECK (tenant_id = current_setting('app.current_tenant'));
```
