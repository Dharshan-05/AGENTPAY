# Phase 131 — Agent Metadata Architecture

## Purpose
Phase 131 introduces a controlled, tenant-isolated metadata layer (`AgentMetadata` ORM model, `agent_metadata` table) for autonomous agents in AGENTPAY.

## Architectural Invariants
- **Tenant Isolation**: All queries enforce `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`.
- **Protected Fields**: Internal fields (`id`, `tenant_id`, `agent_id`, `created_at`, `updated_at`, `status`, `trust_score`) cannot be modified via client metadata payloads.
- **Mass Assignment Defense**: Transport schema `AgentMetadataUpdateRequest` configures `extra="forbid"`.
- **Secret Sanitization**: Zero passwords, raw credentials, secret hashes, API keys, or JWT tokens allowed in JSONB payloads.
- **IDOR Protection**: Cross-tenant attempts return `HTTP 404 Not Found` (`AgentNotFoundError`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/metadata` | `agents:metadata_read` | Retrieve agent JSONB metadata payload |
| PATCH | `/api/v1/agents/{agent_id}/metadata` | `agents:metadata_update` | Update/merge metadata key-value pairs |
