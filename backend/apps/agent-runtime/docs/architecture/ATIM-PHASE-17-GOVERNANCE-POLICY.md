# ATIM Phase 17 — Administrative Governance Policy

## 1. Non-Negotiable Governance Rules
1. **ZERO LLM POLICY AUTHORITY**: Policy creation, approval, activation, suspension, or retirement **MUST NEVER** involve LLM proposals, user prompts, or model outputs.
2. **FOUR-EYES CONTROL**: For protected policies, `creator_id != approver_id`. Creator cannot approve their own submission.
3. **VERSION IMMUTABILITY**: Overwriting active policy configurations is forbidden. All changes yield a new version (`v1`, `v2`, `v3`).
4. **HMAC SIGNATURE INTEGRITY**: All policy lifecycle state transitions generate SHA-256 HMAC cryptographic signatures via `ATIMAuditLockService`.
