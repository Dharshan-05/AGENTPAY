# AGENTPAY Architecture — JWT Authentication (Phase 104)

## Architecture Overview
The AGENTPAY platform implements stateless, cryptographically signed JSON Web Tokens (JWT) for API request authentication, integrated directly with server-side session lifecycle management and tenant isolation boundaries.

## Key Design Principles & Security Controls
1. **Algorithm & Signing**: Signed using HMAC-SHA256 (`HS256`) via PyJWT/python-jose with mandatory key length enforcement (>= 32 characters in production).
2. **Standardized Claims**:
   - `sub`: User UUIDv7
   - `tenant_id`: Multi-tenancy isolation UUID
   - `session_id`: Active Session UUIDv7
   - `type`: Explicitly `"access"` (prevents token type confusion)
   - `jti`: Unique token random identifier UUID
   - `iat`: Timestamp of issuance
   - `exp`: Timestamp of expiration (default: 15 minutes)
   - `iss`: Configured issuer (`agentpay-api`)
   - `aud`: Configured audience (`agentpay-client`)
3. **Session Binding**: Access tokens are strictly bound to active `Session` records in PostgreSQL. Token presentation for revoked or expired sessions immediately fails authentication.
4. **User Status Re-Validation**: At request time, user account status is re-evaluated (`active` required; `suspended`/`disabled` accounts fail authentication even if holding an unexpired JWT).
5. **Secret Protection**: Zero hardcoded secrets, raw tokens, or signing keys exposed in logs, exceptions, or `repr()` representations.
