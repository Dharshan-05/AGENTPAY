# DB-ADR-013: Partial & Composite Database Index Optimization

## Context & Problem Statement
Preventing full table scans on large multi-tenant tables while minimizing write amplification.

## Decision
Create composite indexes on `(tenant_id, status)` and partial indexes on low-volume state rows (`status = 'PENDING'`).

## Consequences & Trade-Offs
* **Benefits**: Sub-10ms query performance on tenant dashboard queries.
* **Trade-Offs**: Requires indexing maintenance overhead.
