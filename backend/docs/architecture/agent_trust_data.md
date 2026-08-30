# Phase 134 — Agent Trust Data Architecture

## Purpose
Phase 134 establishes a foundational, controlled trust-data layer (`AgentTrust` ORM model, `agent_trust` table) for autonomous agents in AGENTPAY.

## Architectural Invariants
- **Controlled Administrative Action**: Trust updates require explicit `agents:trust_update` permission. Standard agent creation and updates cannot alter trust scores.
- **Score Validation**: Numerical trust scores are validated in the decimal range `0.00 <= trust_score <= 100.00` (`InvalidAgentTrustScoreError`).
- **Valid Trust Postures**: `unknown`, `low`, `medium`, `high`, `restricted`.
- **Integrated Observability**: Updating trust posture automatically emits `trust_updated` audit events and `trust_changed` security events.
- **IDOR Protection**: Every query enforces tenant isolation (`WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`). Cross-tenant lookup returns `HTTP 404 Not Found`.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/trust` | `agents:trust_read` | Retrieve agent trust score and posture data |
| PATCH | `/api/v1/agents/{agent_id}/trust` | `agents:trust_update` | Controlled administrative update of trust posture |
