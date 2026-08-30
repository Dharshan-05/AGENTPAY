# Agent Registry API (Phase 119)

## Overview

Phase 119 implements the Agent Registry API for discovering and retrieving registered first-class autonomous agent principals belonging to the authenticated tenant.

## API Endpoints

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| GET | `/api/v1/agents` | `agents:read` | List tenant agents (keyset paginated, searchable) |
| GET | `/api/v1/agents/{agent_id}` | `agents:read` | Get individual agent by ID |

## Architecture

```
FastAPI endpoint
  → require_permission(AGENTS_READ)
  → AgentService.list_agents() / get_agent()
  → SQLAlchemy AsyncSession (WHERE tenant_id = :authenticated_tenant)
```

## Keyset Pagination Strategy

Uses keyset pagination (`cursor_created_at` + `cursor_id`) for $O(1)$ page traversal without database `OFFSET` degradation.

Query ordering: `ORDER BY created_at DESC, id DESC`
Condition: `WHERE (created_at < cursor_created_at OR (created_at = cursor_created_at AND id < cursor_id))`

Filters supported:
- `search`: Case-insensitive substring match against `name` or `slug`
- `agent_type`: Exact filter (e.g. `'autonomous'`)
- `status`: Exact filter (e.g. `'active'`)

Bounded page size: default 20, max 100.

## Tenant Isolation & IDOR Protection

All agent queries explicitly filter by `Agent.tenant_id == authenticated_tenant_id`.

Cross-tenant agent lookup attempts return `HTTP 404 Not Found` via `AgentNotFoundError` to avoid revealing the existence of resources across tenants (anti-enumeration).

## Safe Response Model

`AgentResponse` serializes only non-sensitive agent metadata and non-secret identity fields. Zero credential secrets or token hashes are ever returned.
