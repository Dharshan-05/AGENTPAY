# AGENTPAY — 36: 30 Attack Vector Red-Team Simulation Scenarios

## 1. Red-Team Attack Matrix Overview

This document specifies 30 distinct red-team attack scenarios simulating real-world adversaries, compromised agents, prompt injection exploits, and payment fraud.

---

## 2. 30 Red-Team Attack Scenarios

| Attack ID | Attack Scenario | Target Component | Expected Security Defense | Result |
| :--- | :--- | :--- | :--- | :--- |
| **RED-01** | Stolen User JWT Access Token | User Session | Token expires in 15m; MFA required for sensitive actions | BLOCKED |
| **RED-02** | Stolen Agent HMAC Secret Key | Agent Auth | IP/Geo anomaly detection + User Emergency Revocation | BLOCKED |
| **RED-03** | Agent Impersonation Attack | Agent Gateway | Cryptographic HMAC signature check fails (`ERR_INVALID_SIGNATURE`) | BLOCKED |
| **RED-04** | Agent Privilege Escalation | Agent Scopes | Capability scope check denies unassigned scope (`ERR_SCOPE_DENIED`) | BLOCKED |
| **RED-05** | Direct Prompt Injection Exploit | LLM Agent | AGENTGUARD external policy gate enforces limits outside LLM context | BLOCKED |
| **RED-06** | Indirect Prompt Injection via Web Page | LLM Agent | Untrusted web text isolated in `user` role; policy limits enforced | BLOCKED |
| **RED-07** | Malicious Tool Poisoning | Agent Tools | Schema validation & tool scope allowlist denies unauthorized tool | BLOCKED |
| **RED-08** | Malicious Merchant Domain Spoofing | Merchant API | Domain age & trust score check returns severe risk score penalty | BLOCKED |
| **RED-09** | Replay of Past Valid Intent Request | API Gateway | Redis Nonce cache check rejects duplicate nonce (`ERR_REPLAY_ATTEMPT`) | BLOCKED |
| **RED-10** | Concurrent Duplicate Intent Processing | Payment Service | Distributed Redis lock (`SETNX`) prevents parallel double-spending | BLOCKED |
| **RED-11** | Client-Side Payment Amount Manipulation| Payment Adapter | Amount validated server-side against intent record; client input ignored| BLOCKED |
| **RED-12** | Merchant Identification Spoofing | AGENTGUARD | Server-side MID / MCC verification against verified database | BLOCKED |
| **RED-13** | Webhook Forgery Attack | Webhook Listener | Razorpay HMAC signature verification fails (`X-Razorpay-Signature`) | BLOCKED |
| **RED-14** | Webhook Replay Attack | Webhook Listener | Webhook Event ID idempotency check rejects duplicate event | BLOCKED |
| **RED-15** | BOLA / IDOR Transaction Query | API Gateway | RLS & Tenant ownership context denies access to foreign tenant ID | BLOCKED |
| **RED-16** | SQL Injection via Intent Context | Relational DB | 100% Parameterized queries (Prisma/Drizzle) sanitize raw inputs | BLOCKED |
| **RED-17** | XSS Attack via Agent Purpose Tag | Web Dashboard | React automatic DOM escaping + Content Security Policy (CSP) | BLOCKED |
| **RED-18** | CSRF Attack on Approval Action | Approval Center | HTTP-only `SameSite=Strict` session cookies + Anti-CSRF tokens | BLOCKED |
| **RED-19** | SSRF Attack via Merchant Webhook URL | Network Egress | Egress Firewall rules block access to internal metadata/VPC IPs | BLOCKED |
| **RED-20** | API Rate Limit Abuse (1,000 req/sec) | Edge Gateway | Redis sliding window rate limiter returns HTTP 429 `Too Many Requests`| BLOCKED |
| **RED-21** | Credential Stuffing Attack | Login Endpoint | IP rate limiting + Argon2id work factor + Account lock after 5 fails | BLOCKED |
| **RED-22** | Hardcoded Secret Leakage in Git | CI/CD Pipeline | TruffleHog automated secret scanner blocks commit | BLOCKED |
| **RED-23** | Cross-Tenant Data Access Attempt | Database | PostgreSQL Row-Level Security (RLS) denies access to foreign rows | BLOCKED |
| **RED-24** | ML Model Feature Poisoning | FRAUDGUARD | Feature validation bounds sanitize input anomalies prior to scoring | BLOCKED |
| **RED-25** | ML Feature Weight Manipulation | XAI Engine | Pre-computed feature vectors prevent adversarial text manipulation | BLOCKED |
| **RED-26** | Admin Account Compromise Attempt | Admin Console | Step-Up MFA re-verification required for privileged actions | BLOCKED |
| **RED-27** | Malicious npm Package Supply Chain Attack| CI/CD Pipeline | Lockfile SHA pinning + `npm audit` scanning fails build on CVE | BLOCKED |
| **RED-28** | Container Root Escape Attempt | Docker Engine | Non-root container execution + read-only root filesystem blocks escape| BLOCKED |
| **RED-29** | Emergency Payment Kill Switch Bypass | Payment Service | Server-side Redis flag `user:emergency_stop` checked at execution edge | BLOCKED |
| **RED-30** | Audit Log Tampering Attempt | Relational DB | DB permissions deny `UPDATE`/`DELETE`; SHA-256 block hash breaks | BLOCKED |
