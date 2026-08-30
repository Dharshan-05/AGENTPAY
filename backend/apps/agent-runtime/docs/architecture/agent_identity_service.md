# Agent Identity Service (Phase 121)

## Overview

Phase 121 implements the Agent Identity Service for managing non-secret agent identity profiles. An `AgentIdentity` represents descriptive and classification metadata bound 1-to-1 to an `Agent`.

## API Endpoints

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/identity` | `agents:read` | Retrieve non-secret identity profile |

## Architecture

```
FastAPI endpoint
  → require_permission(AGENTS_READ)
  → AgentIdentityService.get_agent_identity()
  → AgentIdentity ORM (WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant)
```

## Credential Separation & Zero-Secret Guarantee

`AgentIdentity` contains **zero credential material**, passwords, API keys, private keys, or tokens. Credential generation and management strictly belong to **Phase 122 (Agent Credential Service)**.

Identity attributes:
- `id`: UUIDv7 primary key
- `tenant_id`: Multi-tenancy isolation key
- `agent_id`: FK → `agents.id` (1-to-1 unique constraint)
- `display_name`: Human-readable display label
- `identity_type`: Classification string (default `'standard'`)
- `external_reference`: External system reference ID
- `description`: Optional identity description text

## Tenant Isolation & 1-to-1 Uniqueness

1. **Tenant Scope**: All identity queries enforce `WHERE tenant_id = :authenticated_tenant`. Cross-tenant identity requests raise `AgentIdentityNotFoundError` (`HTTP 404`).
2. **Uniqueness**: `agent_identities.agent_id` is constrained unique (`uq_agent_identities_agent_id`). Attempting to add a duplicate identity for an agent raises `AgentIdentityAlreadyExistsError` (`HTTP 409 Conflict`).
