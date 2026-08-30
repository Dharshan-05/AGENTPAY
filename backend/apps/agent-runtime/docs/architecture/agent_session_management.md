# Agent Session Management Architecture (Phase 127)

## Overview

Phase 127 implements secure lifecycle management for sessions belonging to autonomous agents (`AgentSessionService`). Reuses the pre-existing `agent_sessions` table (migration `007_agent_credentials_and_sessions.py`).

## API Endpoints

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/sessions` | `agents:sessions_create` | Create/issue new agent runtime session |
| GET | `/api/v1/agents/{agent_id}/sessions` | `agents:sessions_read` | List agent sessions (keyset paginated) |
| GET | `/api/v1/agents/{agent_id}/sessions/{session_id}` | `agents:sessions_read` | Get safe session metadata by ID |
| POST | `/api/v1/agents/{agent_id}/sessions/{session_id}/revoke` | `agents:sessions_revoke` | Revoke a specific active session |
| POST | `/api/v1/agents/{agent_id}/sessions/revoke-all` | `agents:sessions_revoke` | Bulk revoke all active sessions for agent |

## Security & Defense-in-Depth

1. **Server-Controlled Identifiers & Expiration**: Session IDs are UUIDv7 generated on the server (`uuid.uuid4()`). Session TTL duration is calculated server-side (`expires_at = now + timedelta(hours=ttl)`). Client cannot inject expiration timestamps or session IDs.
2. **Operational State Requirement**: Sessions cannot be created for agents in `"suspended"` or `"deactivated"` states (`AgentSessionCreationError`).
3. **Defense in Depth Session Validation**: `validate_session()` verifies:
   - Session status is `"active"`
   - `now <= session.expires_at`
   - Agent status is active (rejects sessions if agent was suspended/deactivated after session issuance)
4. **Tenant Isolation & IDOR Protection**: Every session query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. For individual sessions: `WHERE id = :session_id AND agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant queries return `HTTP 404 Not Found` (`AgentSessionNotFoundError`).
5. **Keyset Pagination**: Session listing uses cursor-based pagination ordering by `created_at DESC, id DESC`.
6. **Immutable Revocation**: Revoked sessions can never be resurrected. Revocation stores `revoked_at` timestamp and `revocation_reason`.
