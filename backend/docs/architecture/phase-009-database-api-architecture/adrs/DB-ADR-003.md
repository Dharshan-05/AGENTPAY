# DB-ADR-003: Cascading Multi-Tenant Schema Isolation Architecture

## Context & Problem Statement
Preventing cross-tenant data leaks requires enforcing tenant boundaries across all domain entities.

## Decision
Mandate `tenant_id` columns on 100% of tenant-scoped relational tables as foreign keys referencing `tenants(tenant_id)`.

## Consequences & Trade-Offs
* **Benefits**: Enables hardware-enforced tenant filtering in queries and RLS policies.
* **Trade-Offs**: Requires indexing `tenant_id` on all tables.
