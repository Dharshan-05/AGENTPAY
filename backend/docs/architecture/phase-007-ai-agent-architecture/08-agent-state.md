# AGENTPAY — 08: Identity vs Runtime State vs Memory vs Capability Storage

## 1. State Segregation Matrix

To maintain strict security and performance isolation, agent state is partitioned across distinct datastores:

| State Component | Storage Subsystem | Mutability | Persistence TTL | Security Controls |
| :--- | :--- | :--- | :--- | :--- |
| **Agent Identity** | PostgreSQL `agents` table | Immutable GUID | Permanent | Cryptographically bound to `user_id` |
| **Capabilities & Policy**| PostgreSQL + Redis Cache | Admin Mutable | Permanent | Modifiable only by human owner |
| **HMAC Credentials** | Vault / Encrypted DB | Key Rotation | Secret Lifecycle | Argon2id / AES-256-GCM encrypted |
| **Runtime Execution State**| Redis In-Memory Store | Task Mutable | Task Duration | Namespaced by `tenant_id:agent_id` |
| **Conversational Memory**| Redis / LangGraph Checkpoint| Session Mutable | 24 Hours | Scoped by session GUID |
| **Semantic Knowledge RAG**| PostgreSQL + pgvector | Append-Only | Permanent | Scoped by PostgreSQL RLS policies |
