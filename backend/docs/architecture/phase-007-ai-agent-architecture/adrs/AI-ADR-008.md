# AI-ADR-008: PostgreSQL + pgvector Hybrid RAG Architecture

## Context & Problem Statement
External vector databases add operational complexity and require maintaining duplicate tenant authorization models.

## Decision
Use PostgreSQL with `pgvector` extension for hybrid dense vector and sparse keyword search, leveraging PostgreSQL Row-Level Security (RLS) for tenant isolation.

## Consequences & Trade-Offs
* **Benefits**: Single database infrastructure with hardware-enforced tenant data isolation.
* **Trade-Offs**: Requires indexing vector columns with HNSW/IVFFlat indexes.
