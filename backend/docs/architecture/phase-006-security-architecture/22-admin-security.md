# AGENTPAY — 22: Privileged Access Control & Step-Up Auth Workflows

## 1. Privileged Action Step-Up Authentication

High-impact administrative actions (e.g. changing global risk thresholds, rotating HMAC keys, disengaging Emergency Stop) require **Step-Up Authentication**:

1. User re-enters primary password.
2. User provides valid TOTP 6-digit MFA verification code.
3. System verifies `PLATFORM_ADMIN` RBAC permission.
4. System logs privileged action in elevated security audit log.
