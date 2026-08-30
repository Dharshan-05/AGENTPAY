# Phase 145 — Intent Storage Architecture

## Purpose
Phase 145 implements persistent intent storage (`IntentStorageService`) for AGENTPAY, storing normalized intent payloads in the database (`agent_intents` table).

## Database Schema & Invariants
- **Table**: `agent_intents` (Alembic revision `038_agent_intents`).
- **Tenant & Agent Scoping**: Enforces `tenant_id` and `agent_id` isolation on all read and write queries (`AgentNotFoundError` 404 IDOR defense).
- **Atomic Transaction**: Pipeline execution (Extract -> Classify -> Validate -> Normalize -> Store) occurs in a single database transaction.
- **Audit Logging**: Emits `intent_stored` audit events via `AgentAuditService`. Zero secret leakage.
- **Zero Execution**: Stored intents represent validated buyer intent declarations only. MUST NOT execute payments, call tools, or trigger downstream plans.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/intent` | `agents:intent_create` | Process intent pipeline and store normalized intent |
| GET | `/api/v1/agents/{agent_id}/intent/{intent_id}` | `agents:intent_read` | Retrieve stored agent intent by ID |
| GET | `/api/v1/agents/{agent_id}/intents` | `agents:intent_read` | List stored agent intents with keyset pagination |
