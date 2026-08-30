# AGENTPAY — 17: Multi-Tenant Memory Access Control & Retrieval Policies

## 1. Memory Access Security Controls

1. **Row-Level Security**: PostgreSQL vector tables enforce RLS policies: `WHERE tenant_id = current_setting('app.current_tenant')`.
2. **PII Masking**: Customer names, credit card numbers, and auth tokens are stripped prior to vector embedding generation.
3. **Memory Erasure**: Executing user "Right-to-Be-Forgotten" purges semantic vector embeddings and relational history within $< 60\text{ seconds}$.
