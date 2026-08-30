# AGENTPAY — 06: Multi-Tenant Data Hierarchy (`tenant_id` Cascading Scope)

## 1. Multi-Tenant Cascading Hierarchy

$$\text{Tenant} \rightarrow \text{User} \rightarrow \text{Agent} \rightarrow \text{Order} \rightarrow \text{PaymentIntent} \rightarrow \text{Payment} \rightarrow \text{LedgerEntry}$$

Every SQL query initiated by backend repositories automatically injects the tenant isolation context:

```sql
SELECT * FROM payments 
WHERE tenant_id = 'tenant_7f8a9b0c' AND payment_id = 'pay_1a2b3c4d';
```

Cross-tenant joins or queries omitting `tenant_id` fail deterministically.
