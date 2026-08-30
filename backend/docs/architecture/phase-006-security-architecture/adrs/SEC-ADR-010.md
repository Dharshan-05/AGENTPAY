# SEC-ADR-010: PostgreSQL Row-Level Security Tenant Isolation

## Context & Problem Statement
In a multi-tenant platform, application logic bugs could lead to cross-tenant data leakage (BOLA / IDOR).

## Threat Analysis
Tenant A querying `/api/v1/transactions/intent_123` might access Tenant B's data if application-level checks fail.

## Decision
Enforce PostgreSQL Row-Level Security (RLS) policies at the database layer, filtering rows strictly by `tenant_id = current_setting('app.current_tenant')`.

## Consequences & Trade-Offs
* **Benefits**: Database-level isolation prevents cross-tenant access even if application code fails.
* **Trade-Offs**: Connection pools must set tenant session variables prior to query execution.
