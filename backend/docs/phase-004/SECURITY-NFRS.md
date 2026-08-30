# AGENTPAY — Security Non-Functional Requirements

## 1. Overview

Security requirements establish non-negotiable standards for transport encryption, credential hashing algorithms, revocation propagation latency, secrets isolation, and rate limiting defenses.

---

## 2. Requirement Baseline

### NFR-SEC-001: Mandatory TLS 1.3 Transport Encryption
* **NFR ID**: `NFR-SEC-001`
* **Title**: Mandatory Transport Layer Security (TLS 1.3)
* **Source FR**: `FR-AUTH-003`, `REQ-SEC-011`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Security
* **Requirement**: All external HTTP endpoints (User Web Application, Agent API Gateway, Webhooks) shall mandate TLS 1.3 transport encryption. Plain HTTP requests shall be rejected.
* **Rationale**: Protects agent API signatures, JWT session tokens, and payment intents from eavesdropping and tampering.
* **Metric & Target**: $100.0\%$ TLS 1.3 Compliance; Grade A+ SSL Labs configuration.
* **Measurement Method**: Automated vulnerability scan using OWASP ZAP & TestSSL.
* **Acceptance Criteria**: Unencrypted HTTP requests fail with 403 or redirect; cipher suites restricted to AES-256-GCM / CHACHA20-POLY1305.
* **Dependencies**: None.

---

### NFR-SEC-002: Cryptographic Password & Key Hashing Standard
* **NFR ID**: `NFR-SEC-002`
* **Title**: Argon2id Hashing for User Passwords & Agent Key Hashes
* **Source FR**: `FR-AUTH-001`, `FR-AGENT-002`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Security
* **Requirement**: User passwords and agent secret keys shall be stored exclusively in Argon2id hashed format using parameters: $m=65536\text{ KB}$ (64MB), $t=3$ iterations, $p=4$ parallelism.
* **Rationale**: Resistant against offline GPU/ASIC brute-force cracking attempts.
* **Metric & Target**: Argon2id ($m=64\text{MB}, t=3, p=4$); zero plain text storage.
* **Measurement Method**: Source code audit and DB inspection verifying hash prefix `$argon2id$`.
* **Acceptance Criteria**: All credentials stored with valid Argon2id hash signatures.
* **Dependencies**: None.

---

### NFR-SEC-003: Agent Revocation Cache Purge Latency SLA
* **NFR ID**: `NFR-SEC-003`
* **Title**: Instant Agent Revocation Propagation SLA
* **Source FR**: `FR-AGENT-003`, `BR-007`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Agent Security
* **Requirement**: Transitioning an agent state to `REVOKED` shall purge edge Redis authentication keys in $< 10\text{ ms}$, rejecting subsequent API requests immediately.
* **Rationale**: Prevents a compromised agent from executing remaining intent requests after revocation.
* **Metric & Target**: Redis key eviction completed in $< 10\text{ ms}$.
* **Measurement Method**: Real-time latency timer from revocation API call to subsequent test API request rejection.
* **Acceptance Criteria**: API request submitted 15ms after revocation is rejected with `ERR_AGENT_REVOKED`.
* **Dependencies**: Redis edge caching.
