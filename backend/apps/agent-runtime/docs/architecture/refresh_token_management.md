# AGENTPAY Architecture — Refresh Token Management (Phase 106)

## Overview
Refresh tokens in AGENTPAY allow clients to obtain new short-lived access tokens without requiring re-entry of user credentials.

## Lifecycle & Security Controls
1. **Opaque Tokens & One-Way SHA-256 Hashing**:
   - Refresh tokens are 64-byte URL-safe cryptographically random strings (`secrets.token_urlsafe(64)`).
   - Only the SHA-256 hex digest (`token_hash`) is stored in the database. Raw refresh tokens are never persisted or logged.
2. **Token Rotation**:
   - Upon calling `POST /api/v1/auth/refresh`, the presented token status is set to `rotated`.
   - A new active refresh token is generated and linked to the same `family_id` and `parent_token_id`.
3. **Replay Detection & Automatic Revocation**:
   - If an already-rotated token is presented for refresh, the system detects replay/theft.
   - All tokens in the `family_id` and the associated `Session` are immediately revoked.
   - A `refresh_reuse_detected` security event is recorded.
4. **Logout Integration**:
   - Calling `POST /api/v1/auth/logout` revokes the session and sets all associated refresh tokens to `revoked`.
5. **Tenant Isolation**:
   - Refresh token lookup requires matching `tenant_id`. Cross-tenant token presentation is rejected.
