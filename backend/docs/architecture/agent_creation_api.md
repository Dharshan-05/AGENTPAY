# Agent Creation API (Phase 120)

## Overview

Phase 120 implements production-grade agent provisioning. Creating an agent atomically creates both the core `Agent` principal record and its default `AgentIdentity` profile record.

## API Endpoints

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents` | `agents:create` | Create new agent + default identity |

## Architecture

```
FastAPI endpoint
  → require_permission(AGENTS_CREATE)
  → AgentService.create_agent()
  → Atomic AsyncSession Transaction:
      1. Slug uniqueness check within tenant
      2. Instantiate Agent (id=UUIDv7, tenant_id=authenticated_tenant, status='active')
      3. Instantiate AgentIdentity (id=UUIDv7, tenant_id=authenticated_tenant, agent_id=agent.id)
      4. Flush & Refresh
```

## Security & Mass Assignment Protection

Input schema: `AgentCreateRequest` with `ConfigDict(extra="forbid")`.

Client attempts to inject or manipulate the following fields are strictly rejected by the parser:
- `tenant_id`
- `agent_id` / `id`
- `status`
- `trust_score`
- `roles` / `permissions`
- `credentials`
- `created_by`

The tenant binding is sourced strictly from `current_user.tenant_id` (verified JWT session).

## Slug Generation & Uniqueness

If `slug` is omitted in `AgentCreateRequest`, `AgentService` automatically slugifies the agent `name` (URL-safe, lowercase alphanumeric and hyphens). Custom slugs are validated against `^[a-z0-9]+(?:-[a-z0-9]+)*$`.

If a slug collision occurs within the tenant, `AgentAlreadyExistsError` is raised, resulting in `HTTP 409 Conflict`.

## Transaction Atomicity

Agent and identity creation are executed within a single database transaction. If any error occurs, the session rolls back atomically, preventing orphaned records.
