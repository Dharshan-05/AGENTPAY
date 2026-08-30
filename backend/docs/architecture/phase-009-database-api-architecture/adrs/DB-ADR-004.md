# DB-ADR-004: PostgreSQL Row-Level Security (RLS) Enforcement

## Context & Problem Statement
Application-level filtering alone risks data leakage if a developer forgets a `WHERE tenant_id = X` clause.

## Decision
Enable PostgreSQL Row-Level Security (RLS) on all tenant tables, bound to session variable `app.current_tenant`.

## Consequences & Trade-Offs
* **Benefits**: Database hardware-enforced protection against cross-tenant queries.
* **Trade-Offs**: Requires API connection middleware to set session variable on every checkout.
