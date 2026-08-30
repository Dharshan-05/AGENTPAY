# AGENTPAY — 18: PostgreSQL + pgvector Hybrid RAG Pipeline Specifications

## 1. RAG Retrieval Pipeline

```mermaid
graph TD
    QUERY[User Query / Product Search] --> EMBED[Generate Text Embedding: text-embedding-3-small]
    EMBED --> SIM[pgvector Cosine Similarity Search]
    SIM --> RERANK[Cross-Encoder Reranker]
    RERANK --> FILTER[Filter by tenant_id & Access Policy]
    FILTER --> CONTEXT[Inject Context into LLM Prompt]
```

---

## 2. Document Metadata Schema

Every vector record stores structured security metadata: `{ "tenant_id": "tenant_123", "source_id": "doc_456", "trust_level": "EXTERNAL", "access_policy": "POLICY_PUBLIC" }`.
