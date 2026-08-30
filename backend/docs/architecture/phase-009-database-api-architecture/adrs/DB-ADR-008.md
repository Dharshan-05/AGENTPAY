# DB-ADR-008: Relational Idempotency Record Storage

## Context & Problem Statement
Preventing double-spend events under Redis cache evictions requires durable relational deduplication storage.

## Decision
Store idempotency records in PostgreSQL `idempotency_records` with a unique constraint `UNIQUE(tenant_id, operation, idempotency_key)`.

## Consequences & Trade-Offs
* **Benefits**: 100% durable protection against duplicate execution even during Redis outages.
* **Trade-Offs**: Requires periodic cleanup of expired 24-hour idempotency rows.
