# AGENTPAY — 95: 70 Combined Database & API Red-Team Attack Scenarios

## 1. 70 Master Red-Team Attack Matrix

| Attack ID | Attack Vector | Component Target | Control Defense | Result |
| :--- | :--- | :--- | :--- | :--- |
| **DB-RED-01**| Cross-Tenant Row Query | PostgreSQL DB | PostgreSQL RLS policy `USING(tenant_id)` denies rows | BLOCKED |
| **DB-RED-02**| Cross-Tenant Data Update | PostgreSQL DB | PostgreSQL RLS policy `WITH CHECK(tenant_id)` denies write | BLOCKED |
| **DB-RED-03**| RLS Policy Bypass Attempt | DB Connection Pool | Connection uses restricted non-superuser role `agentpay_app` | BLOCKED |
| **DB-RED-04**| SQL Injection via Path Param | API Repository | Parameterized SQL query placeholder `$1` neutralizes injection | BLOCKED |
| **DB-RED-05**| App Role Escalation | PostgreSQL Role | Role permissions deny `GRANT` & `ALTER TABLE` DDL queries | BLOCKED |
| **DB-RED-06**| Ledger Entry Mutation | `ledger_entries` | DB permission revokes `UPDATE` and `DELETE` on ledger tables | BLOCKED |
| **DB-RED-07**| Un-Authorized Payment State Set| `payment_intents` | State transition check trigger blocks invalid state jump | BLOCKED |
| **DB-RED-08**| Refund Exceeding Payment | `refunds` | DB check constraint `sum(refunds) <= payment_amount` fails | BLOCKED |
| **DB-RED-09**| Idempotency Key Collision | `idempotency_records`| DB unique constraint `uq_idempotency_tenant_key` rejects | BLOCKED |
| **DB-RED-10**| Duplicate Payment Clearing | `payments` | DB unique constraint `provider_payment_id` rejects duplicate | BLOCKED |
| **DB-RED-11**| Parallel Race Condition | Payment Service | `SELECT FOR UPDATE` pessimistic row lock forces serial execution | BLOCKED |
| **DB-RED-12**| Deadlock Exploitation | Transaction Engine | Deadlock timeout (1s) aborts & application retries safely | BLOCKED |
| **DB-RED-13**| Migration Script Corruption | CI/CD Migrator | Migration checksum verification fails build pipeline | BLOCKED |
| **DB-RED-14**| Unencrypted Backup Theft | Backup Storage | S3 SSER-KMS AES-256 encryption renders backup unreadable | BLOCKED |
| **DB-RED-15**| Database Credential Leak | Application App | Secrets stored in Vault; injected via ephemeral RAM tokens | BLOCKED |
| **DB-RED-16**| Audit Event Truncation | `audit_events` | DB permission revokes `DELETE` and `TRUNCATE` | BLOCKED |
| **DB-RED-17**| Outbox Message Tampering | `outbox_events` | SHA-256 event hash mismatch rejects outbox delivery | BLOCKED |
| **DB-RED-18**| Event Replay Attack | Event Consumer | Consumer checks `event_deliveries` unique constraint | BLOCKED |
| **DB-RED-19**| Webhook Payload Injection | `webhook_events` | Signature check fails before DB insertion | BLOCKED |
| **DB-RED-20**| Provider Payment ID Forgery | `payments` | Foreign key check fails against verified provider attempt | BLOCKED |
| **DB-RED-21**| Tenant ID Spoofing in Query | API Repository | Server extracts `tenant_id` strictly from JWT claims | BLOCKED |
| **DB-RED-22**| Agent ID Forgery in Intent | `payment_intents` | Foreign key & capability scope check rejects unassigned agent | BLOCKED |
| **DB-RED-23**| User ID Forgery in Order | `orders` | Foreign key check against verified authenticated user ID | BLOCKED |
| **DB-RED-24**| Mass Assignment Field Attack | API Gateway | Zod schema `.strict()` strips unexpected request body fields | BLOCKED |
| **DB-RED-25**| Sequential ID Enumeration | API Ingress | UUID v4 random IDs prevent numeric ID enumeration | BLOCKED |
| **DB-RED-26**| Rate Limit Bypass Attempt | API Gateway | Redis sliding-window IP & Tenant rate limits block flood | BLOCKED |
| **DB-RED-27**| Redis Cache Poisoning | Redis Cache | Redis contains non-authoritative read data only; DB verifies | BLOCKED |
| **DB-RED-28**| Stale Financial Read Exploitation| Payment Service | Critical settlement reads force fresh PostgreSQL SELECT | BLOCKED |
| **DB-RED-29**| Policy Version Tampering | `policy_versions` | Immutable version records reject modification | BLOCKED |
| **DB-RED-30**| Risk Score Tampering | `risk_assessments` | Risk score populated exclusively by server-side FastAPI | BLOCKED |
| **DB-RED-31**| Human Approval Spoofing | `approval_requests` | Approval action validates JWT user signature against card ID | BLOCKED |
| **DB-RED-32**| Auth Context Token Replay | `payment_authorizations`| Single-use token eviction from Redis post-dispatch | BLOCKED |
| **DB-RED-33**| Out-of-Order Event Attack | Event Worker | Event sequence number check buffers out-of-order payloads | BLOCKED |
| **DB-RED-34**| Database Role Abuse | Application App | Restricted DB connection pool role blocks admin commands | BLOCKED |
| **DB-RED-35**| Direct DB API Exposure | API Gateway | Repositories encapsulate DB; zero raw SQL endpoints exposed | BLOCKED |
| **API-RED-36**| JWT Signature Forgery | Auth Middleware | RS256 public key verification rejects forged signature | BLOCKED |
| **API-RED-37**| Expired JWT Submission | Auth Middleware | Expiration timestamp claim check (`exp < NOW()`) fails | BLOCKED |
| **API-RED-38**| Missing Auth Header | Auth Middleware | Returns HTTP 401 Unauthorized immediately | BLOCKED |
| **API-RED-39**| Unassigned Capability Scope | AGENTGUARD API | Scope check `spend:intent_create` fails (`HTTP 403`) | BLOCKED |
| **API-RED-40**| Cross-Tenant API Object Access| API Gateway | Tenant context check (`token.tenant_id != resource.tenant_id`) | BLOCKED |
| **API-RED-41**| Client Tenant Header Override| API Gateway | Ingress ignores `X-Tenant-ID` header; uses JWT claim | BLOCKED |
| **API-RED-42**| Arbitrary Status PATCH Call | Router | Endpoint `PATCH /payments/{id}` returns HTTP 405 | BLOCKED |
| **API-RED-43**| Client Risk Score Injection | Payment API | `risk_score` stripped from request body payload | BLOCKED |
| **API-RED-44**| Client Ledger Balance Set | Ledger API | Public ledger write API endpoints do not exist | BLOCKED |
| **API-RED-45**| Webhook HMAC Forgery | Webhook API | HMAC-SHA256 signature verification fails (`HTTP 401`) | BLOCKED |
| **API-RED-46**| Webhook Replay (Duplicate Event)| Webhook API | Redis 7-day event ID check ignores duplicate (`HTTP 200`) | BLOCKED |
| **API-RED-47**| Webhook Payload Alteration | Webhook API | Raw payload signature check fails on altered body | BLOCKED |
| **API-RED-48**| Retrying UNKNOWN State API | Payment API | Execution API rejects attempts on `UNKNOWN` status | BLOCKED |
| **API-RED-49**| Refund Exceeding Balance API | Refund API | Server-side balance calculation rejects request (`HTTP 422`)| BLOCKED |
| **API-RED-50**| Idempotency Key Reuse Mutation | API Gateway | Request hash comparison fails (`HTTP 409 Conflict`) | BLOCKED |
| **API-RED-51**| API Rate Limit Flood | Rate Limiter | Sliding-window limiter blocks flood (`HTTP 429`) | BLOCKED |
| **API-RED-52**| Unsigned Agent Intent Proposal| Gateway Edge | HMAC signature check `X-Agent-Signature` fails (`HTTP 401`) | BLOCKED |
| **API-RED-53**| Agent Signature Timestamp Replay| Gateway Edge | Signature timestamp window ($> 300\text{s}$) rejects replay | BLOCKED |
| **API-RED-54**| CORS Domain Hijacking | API Gateway | CORS whitelist restricts origins strictly to approved domains| BLOCKED |
| **API-RED-55**| Payload Oversize DoS Attack | Gateway Edge | Ingress body size limited to 100 KB max (`HTTP 413`) | BLOCKED |
| **API-RED-56**| Arbitrary File Path Traversal | API Gateway | Static file serving disabled; path sanitization enforced | BLOCKED |
| **API-RED-57**| Un-Whitelisted Query Filter | API Controller | Un-whitelisted query params stripped/rejected (`HTTP 400`) | BLOCKED |
| **API-RED-58**| Un-Whitelisted Sort Parameter | API Controller | Un-whitelisted sort fields rejected (`HTTP 400`) | BLOCKED |
| **API-RED-59**| Deep Offset Pagination DoS | API Controller | Deep offset banned; cursor-based pagination enforced | BLOCKED |
| **API-RED-60**| Mass Assignment Role Injection| API Controller | Protected fields stripped by Zod `.strict()` schema | BLOCKED |
| **API-RED-61**| Stack Trace Secret Leakage | Error Middleware | Internal errors sanitized to generic error code responses | BLOCKED |
| **API-RED-62**| Unencrypted HTTP API Connection| Gateway Edge | HTTP requests redirected to HTTPS (TLS 1.3 enforced) | BLOCKED |
| **API-RED-63**| Admin Endpoint Escalation | Router | Admin endpoints check `role == ADMIN` claims | BLOCKED |
| **API-RED-64**| Emergency Kill Switch Bypass | Payment API | Redis `killswitch` flag check halts processing (`HTTP 503`) | BLOCKED |
| **API-RED-65**| Forged Approval Token | Approval API | Approval JWT signature verification fails | BLOCKED |
| **API-RED-66**| Expired Approval Token Reuse | Approval API | Token single-use eviction check rejects reused token | BLOCKED |
| **API-RED-67**| Provider Secret API Key Leak | Response Filter | Gateway credentials excluded from API responses | BLOCKED |
| **API-RED-68**| Floating-Point Rounding Exploitation| Payment API | Integer minor units enforce exact mathematical balance | BLOCKED |
| **API-RED-69**| Double-Entry Ledger Imbalance | Accounting API | Trigger functions verify $\sum \text{Debit} = \sum \text{Credit}$ | BLOCKED |
| **API-RED-70**| Multi-Agent Collusion Bypass | Orchestrator | Every agent intent proposal passes independent AGENTGUARD gate| BLOCKED |
