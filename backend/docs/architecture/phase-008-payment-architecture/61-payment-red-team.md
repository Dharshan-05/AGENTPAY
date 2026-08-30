# AGENTPAY — 61: 35 Payment Red-Team Attack Simulation Scenarios

## 1. 35 Payment Red-Team Attack Scenarios

| Attack ID | Attack Scenario | Target Component | Security Defense Control | Result |
| :--- | :--- | :--- | :--- | :--- |
| **PAY-RED-01**| Parallel Double-Spend Attempt | Payment Service | Redis 24h `SETNX` lock + PostgreSQL unique constraint | BLOCKED |
| **PAY-RED-02**| Replay of Expired Auth Token | Payment Orchestrator | Auth token 15m expiration TTL check fails (`ERR_TOKEN_EXPIRED`) | BLOCKED |
| **PAY-RED-03**| Amount Mutation in Flight | Razorpay Adapter | Amount validated server-side against signed auth token | BLOCKED |
| **PAY-RED-04**| Currency Substitution (INR -> USD)| Provider Adapter | Currency validated against signed auth token | BLOCKED |
| **PAY-RED-05**| Merchant MID Substitution | Payment Intent | Verified MID mapping lookup fails (`ERR_INVALID_MERCHANT`) | BLOCKED |
| **PAY-RED-06**| Order ID Forgery | Payment Service | Foreign order ownership check fails | BLOCKED |
| **PAY-RED-07**| Stolen Auth Token Reuse | Payment Orchestrator | Auth token single-use eviction from Redis | BLOCKED |
| **PAY-RED-08**| Replay of Used Auth Token | Payment Orchestrator | State machine transition check (`State != AUTHORIZED`) | BLOCKED |
| **PAY-RED-09**| Expired Auth Token Submission | Payment Orchestrator | Expiration timestamp check (`expires_at < NOW()`) | BLOCKED |
| **PAY-RED-10**| Agent Privilege Escalation | AGENTGUARD | Scoped capability check (`spend:intent_create`) fails | BLOCKED |
| **PAY-RED-11**| Agent Impersonation | Gateway Edge | HMAC signature header check (`X-Agent-Signature`) fails | BLOCKED |
| **PAY-RED-12**| Direct Razorpay Settlement Call| External Rails | Razorpay secret API keys isolated in backend container | BLOCKED |
| **PAY-RED-13**| Fake Webhook Event Ingestion | Webhook Listener | Razorpay HMAC signature verification fails (`X-Razorpay-Signature`)| BLOCKED |
| **PAY-RED-14**| Webhook Replay Attack | Webhook Listener | Event ID idempotency deduplication check rejects duplicate | BLOCKED |
| **PAY-RED-15**| Webhook Payload Mutation | Webhook Listener | Signature mismatch rejects mutated raw payload | BLOCKED |
| **PAY-RED-16**| Provider Timeout Exploitation | Gateway Edge | Timeout transitions state to `PAYMENT_STATUS_UNKNOWN` (No retry)| BLOCKED |
| **PAY-RED-17**| Retrying UNKNOWN Payment State | Retry Engine | Retry engine blocks attempts on `UNKNOWN` state | BLOCKED |
| **PAY-RED-18**| Refund Overflow (Refund > Amount)| Refund Service | Balance check (`Requested > RefundableBalance`) fails | BLOCKED |
| **PAY-RED-19**| Refund Replay Attempt | Refund Service | Redis 24h idempotency lock on refund request | BLOCKED |
| **PAY-RED-20**| Unauthorized Refund Request | Refund Service | Capability scope check (`refund:request`) fails | BLOCKED |
| **PAY-RED-21**| Cross-Tenant Payment Query | API Gateway | PostgreSQL RLS policy denies access to foreign tenant rows | BLOCKED |
| **PAY-RED-22**| Payment ID Enumeration | API Gateway | Random UUID v4 identifiers prevent sequence enumeration | BLOCKED |
| **PAY-RED-23**| Idempotency Key Collision | Ingress Gateway | Redis payload hash comparison rejects mismatched body | BLOCKED |
| **PAY-RED-24**| Concurrent Race on Budget Cap | AGENTGUARD | Atomic Redis `INCRBY` / DB `FOR UPDATE` lock | BLOCKED |
| **PAY-RED-25**| Out-of-Order Webhook Processing | Event Handler | Sequence number check buffers out-of-order events | BLOCKED |
| **PAY-RED-26**| Event Worker Event Loss | Event Bus | Transactional Outbox pattern guarantees atomic dispatch | BLOCKED |
| **PAY-RED-27**| Double-Entry Ledger Imbalance | Ledger Engine | Database check constraint (`Sum(Debit) = Sum(Credit)`) | BLOCKED |
| **PAY-RED-28**| Emergency Kill Switch Bypass | Payment Orchestrator | Server-side Redis flag `user:emergency_stop` checked at edge | BLOCKED |
| **PAY-RED-29**| Single Limit Policy Cap Bypass | AGENTGUARD | Deterministic rule rule `amount <= limit` fails | BLOCKED |
| **PAY-RED-30**| High Risk Score Bypass (Score > 70)| AGENTGUARD | Rule check `risk_score <= 70` returns `BLOCK` | BLOCKED |
| **PAY-RED-31**| Human Approval Card Replay | Approval Center | Single-use approval token evicted post-click | BLOCKED |
| **PAY-RED-32**| Approval Token Forgery | Approval Center | JWT signature verification fails | BLOCKED |
| **PAY-RED-33**| Hardcoded Secret Exposure in Git | CI/CD Pipeline | TruffleHog automated secret scanner blocks commit | BLOCKED |
| **PAY-RED-34**| Frontend Secret Access Attempt | Frontend App | Secret API keys stored strictly in private backend Vault | BLOCKED |
| **PAY-RED-35**| Floating-Point Rounding Exploitation| Financial Engine| Minor unit integer math eliminates rounding drift | BLOCKED |
