# AGENTPAY Architecture — Logout & Session Revocation (Phase 110)

## Overview
Logout and session revocation in AGENTPAY ensure complete server-side invalidation of authenticated user sessions and refresh tokens.

## Key Design Principles & Security Controls
1. **Server-Side Revocation**: Calling `POST /api/v1/auth/logout` sets the `Session.status` to `"revoked"` and `revoked_at` to the current UTC timestamp.
2. **Refresh Token Revocation**: All `RefreshToken` records associated with the revoked session are marked `"revoked"`.
3. **Access Token Invalidation**: Access tokens present the `session_id` in claims. On protected requests, `get_current_user` checks session status in database and immediately rejects access tokens associated with revoked sessions.
4. **Idempotency**: Repeated logout requests on an already-revoked session execute safely and return a standardized HTTP 200 success response.
5. **Transactional Integrity**: Session revocation and refresh token revocation execute atomically within a single database transaction.
6. **Logout All Sessions Support**: `logout_all_sessions()` allows revoking all active sessions for a user within a tenant scope upon critical security events.
7. **Security Events**: Logs `logout_success`, `session_revoked`, and `logout_all_success` audit events without exposing tokens or secrets.
