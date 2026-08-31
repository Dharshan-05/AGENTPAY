# ATIM Phase 20 — Compliance Evidence & Forensic Auditability Policy

## 1. Core Compliance Rules
1. **APPEND-ONLY IMMUTABILITY**: Compliance evidence records are strictly append-only. APIs or service operations **MUST NOT** provide overwrite or delete functionality.
2. **CRYPTOGRAPHIC HMAC PROTECTION**: All compliance evidence records generate SHA-256 HMAC cryptographic signatures via `ATIMAuditLockService`. Tampered evidence entries are detected immediately during verification.
3. **COMPLETE DECISION LINEAGE**: Preserves full structured execution metadata (`WHO`, `WHAT`, `WHEN`, `TENANT`, `AGENT`, `CORRELATION_ID`, `PRECEDENCE`, `SIGNATURE`) without exposing unredacted raw secrets or PII.
4. **FAIL-CLOSED AUDIT**: If mandatory audit logging infrastructure fails, execution path defaults to `DENY` / `503 Service Unavailable`.
