# AGENTPAY — 03: STRIDE Threat Model & Attack Tree Analysis

## 1. STRIDE Matrix Overview

| Threat Category | Target Asset | Attack Vector | Security Control Defense | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Agent Identity | Stolen HMAC Secret / Replay | HMAC-SHA256 Signatures, Nonce Caching, Timestamp Expiration | HIGH |
| **Tampering** | Payment Intent Payload | HTTP Request Manipulation | Signed Payload Canonical Hashing, TLS 1.3 | CRITICAL |
| **Repudiation** | Authorization Decision| User/Agent denies transaction | Immutable Block Hash Audit Logging (SHA-256 Chain) | MEDIUM |
| **Information Leakage**| Banking Credentials | LLM Context Leakage / Logs | Zero Credential Exposure to LLM; Log Masking | CRITICAL |
| **Denial of Service** | API Gateway | API Flood / Infinite Agent Loop | Multi-Tier Redis Rate Limiting, Circuit Breakers | HIGH |
| **Elevation of Privilege**| Agent Capability Scope| Prompt Injection Attack | AGENTGUARD External Policy Gates, Scoped Capabilities | CRITICAL |

---

## 2. Attack Tree Analysis: Unauthorized Agent Payment

```
                                [ Unauthorized Payment Execution ]
                                                │
       ┌────────────────────────────────────────┴────────────────────────────────────────┐
       ▼                                                                                 ▼
 [ Bypass Agent Authenticator ]                                                [ Prompt Injection Exploit ]
       │                                                                                 │
 ┌─────┴─────┐                                                                     ┌─────┴─────┐
 ▼           ▼                                                                     ▼           ▼
[Replay]   [Stolen Key]                                                        [Hijack]    [Tool Abuse]
 (Blocked:   (Blocked:                                                          (Blocked:   (Blocked:
  Nonce)      Revocation)                                                       Policy Gate) Scopes)
```
