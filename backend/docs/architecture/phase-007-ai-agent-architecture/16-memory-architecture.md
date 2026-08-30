# AGENTPAY — 16: Short-Term, Long-Term, Semantic & Episodic Memory Stores

## 1. Memory Subsystem Architecture

```
+-----------------------------------------------------------------------+
|                         MEMORY SUBSYSTEMS                             |
+-----------------------------------------------------------------------+
|  1. Short-Term Memory  : Redis Session Cache (24h TTL Conversation)  |
|  2. Long-Term Memory   : PostgreSQL Relational User Preferences       |
|  3. Episodic Memory    : Historical Transaction Receipts & Traces     |
|  4. Semantic Memory    : PostgreSQL + pgvector Vector Embeddings       |
+-----------------------------------------------------------------------+
```

---

## 2. Memory Isolation Rule

Memory reads and vector retrieval queries strictly require `tenant_id` context injection, preventing cross-tenant memory leakage.
