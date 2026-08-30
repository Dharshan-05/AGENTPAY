# AGENTPAY Architecture — Session Management (Phase 109)

## Overview
Session management in AGENTPAY maintains server-side, tenant-bound session records in PostgreSQL to track authenticated user contexts across devices and clients.

## Key Design Principles & Security Controls
1. **Unpredictable UUIDv7 Identifiers**: Every session has a unique, unpredictable primary key (`Session.id`).
2. **Tenant & User Binding**: Every session is bound to `tenant_id` and `user_id` with strict database FK constraints (`ondelete="RESTRICT"`).
3. **Session Expiration**: Configurable duration (default: 24 hours). Expired sessions are rejected at authentication time.
4. **Multi-Session Support**: A user can maintain multiple active sessions across different browsers or devices. Revoking one session leaves other active sessions unaffected.
5. **Non-Sensitive Client Metadata**: Stores IP address, User-Agent, device ID, and `last_activity_at` for auditability without storing raw credentials or tokens.
6. **Security Events**: Logs `session_created`, `session_expired`, `session_revoked`, and `session_invalid` security events.
