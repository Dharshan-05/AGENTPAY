# AGENTPAY — 07: User MFA & Agent Cryptographic HMAC Authentication

## 1. Authentication Specifications

### 1.1 User Authentication
* **Primary Credentials**: Argon2id hashed passwords ($m=64\text{MB}, t=3, p=4$).
* **Multi-Factor Authentication**: TOTP RFC 6238 6-digit verification code mandatory for login and policy changes.
* **Session Tokens**: JWT access tokens (15-minute TTL) + HTTP-only secure refresh tokens (7-day TTL).

### 1.2 Agent Authentication
* **Header Structure**: `X-Agent-ID`, `X-Agent-Timestamp`, `X-Agent-Nonce`, `X-Agent-Signature`.
* **Signature Algorithm**: HMAC-SHA256 over canonical string `AgentID:Timestamp:Nonce:Method:Path:SHA256(Body)`.
* **Replay Protection**: Nonce cached in Redis for 15 minutes; timestamps older than 300s rejected.
* **Execution**: Constant-time signature comparison using `crypto.timingSafeEqual`.
