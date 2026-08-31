# ATIM Phase 18 — Rate Limit, Quota & Abuse Prevention Policy

## 1. Core API Protection Rules
1. **Pre-Execution Rate Limiting**: Rate limit and quota checks **MUST** evaluate prior to invoking expensive LLM or database operations.
2. **Decimal Quota Accounting**: Financial quota thresholds and token cost allocations use strict `Decimal` / PostgreSQL `NUMERIC` precision. Floating-point calculations are prohibited.
3. **Deterministic Abuse Escalation**: Abuse detection escalates deterministically (`THROTTLE` $\rightarrow$ `PERMANENT_SECURITY_BLOCK`). LLMs or client inputs **MUST NEVER** control abuse severity or block decisions.
4. **Fail-Closed Availability**: If mandatory rate limiting or Redis enforcement fails, security-sensitive financial paths fail closed (`503 Service Unavailable`).
