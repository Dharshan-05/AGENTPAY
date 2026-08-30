# Phase 132 — Agent Audit Events Architecture

## Purpose
Phase 132 implements reliable, append-only, immutable audit trail functionality (`AgentAudit` ORM model, `agent_audit` table) for security-sensitive agent operations in AGENTPAY.

## Architectural Invariants
- **Immutable Log History**: Zero UPDATE or DELETE endpoints provided by design.
- **Tenant Scope & IDOR Protection**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant requests return `HTTP 404 Not Found`.
- **Keyset Pagination**: Pagination orders by `occurred_at DESC, id DESC` to optimize large audit log queries.
- **Context & Sanitization**: Automatically captures `request_id`, `actor_id`, `ip_address`, and `user_agent`. Redacts raw credentials, secret hashes, and access tokens before persisting.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/audit-events` | `agents:audit_read` | List paginated immutable audit records for an agent |
