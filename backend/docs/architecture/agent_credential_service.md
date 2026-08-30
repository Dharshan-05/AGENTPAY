# Agent Credential Service (Phase 122)

## Overview

Phase 122 implements the Agent Credential Service for managing cryptographically secure secret verification records for autonomous agents. Secrets are stored strictly as one-way cryptographic digests (SHA-256) and raw secrets are returned **ONLY ONCE** upon issuance.

## API Endpoints

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/credentials` | `agents:credential_create` | Issue new credential (raw secret returned ONCE) |
| GET | `/api/v1/agents/{agent_id}/credentials` | `agents:credential_read` | List credential metadata (NO secret material) |
| GET | `/api/v1/agents/{agent_id}/credentials/{credential_id}` | `agents:credential_read` | Get credential metadata (NO secret material) |

## Secret Generation & Cryptographic Storage

1. **CSPRNG Generation**: Raw secret tokens are generated using Python's `secrets.token_urlsafe(32)` (CSPRNG) with prefix `ap_ag_`. Never uses predictable strings, random, timestamps, or UUIDs as secrets.
2. **One-Way Hashing**: Plaintext credentials are **never stored** in database records. Only the one-way SHA-256 cryptographic digest (`secret_hash`) is persisted in `agent_credentials`.
3. **Single Delivery**: The plaintext `raw_secret` string is returned ONCE in `AgentCredentialCreateResponse`. Standard GET metadata endpoints return `AgentCredentialResponse` which strictly excludes secret values and digests.
4. **Constant-Time Verification**: Secret verification uses `secrets.compare_digest(hash_token(provided_secret), stored_hash)` to eliminate timing side-channel attacks.

## Database Model

Reused existing `agent_credentials` table (migration `007_agent_credentials_and_sessions.py`):
- `id`: UUIDv7 primary key
- `tenant_id`: Multi-tenancy isolation key (indexed)
- `agent_id`: FK → `agents.id` (RESTRICT)
- `credential_type`: Credential classification string (e.g. `'api_key'`)
- `credential_identifier`: Public lookup identifier (indexed)
- `secret_hash`: One-way SHA-256 digest string
- `status`: Lifecycle status (`'active'`, `'revoked'`, `'expired'`)
- `expires_at`: Expiration timestamp

## Tenant Isolation & Security Controls

- **Tenant Scope**: All queries filter by `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant`.
- **IDOR Protection**: Cross-tenant credential requests return `HTTP 404 Not Found` (`AgentCredentialNotFoundError`).
- **Redaction**: `AgentCredential.__repr__` redacts `secret_hash`. Log statements omit secret values.
