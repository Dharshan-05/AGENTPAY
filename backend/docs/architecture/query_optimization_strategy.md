# AGENTPAY Query Optimization Strategy Architecture (Phase 077)

## Executive Summary

This document formalizes the production-grade query optimization strategy for **AGENTPAY** (`Phase 077`).

The database access layer has been audited and structured to enforce:
- Mandatory tenant-isolation filtering on every query
- Keyset (cursor-based) pagination (`paginate_keyset`) for high-volume audit, event, and payment streams
- SQL `EXISTS` probes (`check_exists`) instead of loading full rows into Python memory
- Prevention of N+1 query patterns using explicit SQLAlchemy loading options (`joinedload`, `selectinload`)
- Preserved `Decimal` financial/risk score precision and zero unindexed full-table scans

---

## 1. Core Optimization Strategies & Patterns

### 1.1 Mandatory Tenant Isolation
Every query MUST enforce `tenant_id == <tenant_uuid>`. The query builder ([query_builder.py](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/query_builder.py)) enforces tenant isolation at statement construction time.

### 1.2 Keyset (Cursor) Pagination
High-cardinality tables (`audit_logs`, `security_events`, `payment_transactions`, `commerce_transactions`) use deterministic keyset pagination:
```sql
WHERE (created_at < :cursor_created_at) OR (created_at = :cursor_created_at AND id < :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT :limit
```
This eliminates PostgreSQL `OFFSET` performance degradation on deep pages.

### 1.3 Optimized Existence Probes
Existence checks use `SELECT EXISTS(SELECT 1 FROM <table> WHERE tenant_id = :tenant_id AND ...)` returning a lightweight boolean scalar rather than initializing ORM instances.

---

## 2. N+1 Prevention & Loading Rules

- **ToOne Relationships**: Use `joinedload` for mandatory parent lookups (e.g. `order -> merchant`).
- **ToMany Relationships**: Use `selectinload` for collection loading to eliminate Cartesian product explosion.
