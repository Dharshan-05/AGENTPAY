# Phase 133 — Agent Security Events Architecture

## Purpose
Phase 133 provides security event logging and observability (`SecurityEvent` ORM model, `security_events` table) for agent authentication, authorization, credential lifecycle, session activity, and suspension/revocation events in AGENTPAY.

## Architectural Invariants
- **Append-Only Security Log**: Security events are append-only. No UPDATE or DELETE API endpoints exist.
- **Tenant Isolation**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant lookup returns `HTTP 404 Not Found`.
- **Sanitized Payloads**: Payload contexts redact passwords, tokens, raw credentials, and private keys.
- **Keyset Pagination**: Pagination orders by `occurred_at DESC, id DESC`.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/security-events` | `agents:security_events_read` | List paginated security events for an agent |
