# ATIM Phase 18 Architecture — Production API Hardening, Rate Limiting, Quotas & Abuse Prevention

## Executive Summary
**ATIM Phase 18** implements an API protection, rate limiting, quota management, and abuse escalation engine for **AgentPay Transaction Intelligence Model (ATIM)**.

Phase 18 features:
1. **Sliding Window Rate Limiter (`ATIMRateLimiter`)**: Redis-backed atomic sliding window rate limiting evaluated by `tenant_id`, `agent_id`, and `endpoint` dimensions. Returns HTTP 429 with `retry_after`.
2. **Enterprise Quota Engine (`ATIMQuotaService`)**: Strict `Decimal` quota limits for requests/min, requests/day, tokens/day, and cost/day per tenant and agent.
3. **Abuse Prevention Engine (`ATIMAbuseDetectionService`)**: Continuous abuse scoring tracking repeated prompt injections, authentication failures, and rate-limit violations. Escalates through ladder: `THROTTLE` $\rightarrow$ `TEMPORARY_BLOCK` $\rightarrow$ `REQUIRE_HITL` $\rightarrow$ `PERMANENT_SECURITY_BLOCK`.
4. **Authoritative Decision Precedence**:
   `SECURITY BLOCK > PLAN INVALID > AGENTGUARD DENY > FRAUDGUARD BLOCK > QUOTA DENY > RATE LIMIT DENY > HITL REQUIRED > ALLOW`

---

## API Protection Architecture

```text
CLIENT REQUEST
      │
      ▼
AUTHENTICATION & TENANT RESOLUTION
      │
      ▼
RATE LIMIT CHECK (Sliding Window / Redis) ────► Exceeded: HTTP 429
      │
      ▼
QUOTA CHECK (Decimal Precision) ─────────────► Exceeded: HTTP 429 / Quota Denied
      │
      ▼
ABUSE PREVENTION FILTER ──────────────────────► Violation: Escalated Action
      │
      ▼
ATIM PIPELINE EXECUTION
```
