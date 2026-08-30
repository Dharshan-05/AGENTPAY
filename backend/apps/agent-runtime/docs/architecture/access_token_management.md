# AGENTPAY Architecture — Access Token Management (Phase 105)

## Overview
Access tokens in AGENTPAY provide short-lived, secure Bearer token authorization for protected API endpoints.

## Lifecycle & Verification Controls
1. **Issuance**: Issued upon successful `POST /api/v1/auth/login` or `POST /api/v1/auth/refresh`.
2. **Short Lifespan**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 15 minutes).
3. **Bearer Authorization Header**: Passed as `Authorization: Bearer <token>`.
4. **Current User Endpoint**: `GET /api/v1/auth/me` returns safe user identity and profile metadata, verifying Bearer token, session status, user status, and tenant isolation.
5. **Standardized Exception Handling**: Token invalidity or expiration triggers standardized HTTP 401 Unauthorized responses without exposing internal error tracebacks.
