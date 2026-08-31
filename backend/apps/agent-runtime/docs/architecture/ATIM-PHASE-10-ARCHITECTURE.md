# ATIM Phase 10 Architecture — Production REST API Controller, Real-Time Observability & Persistence Engine

## Executive Summary
**ATIM Phase 10 (Group 5)** completes the production deployment of the **AgentPay Transaction Intelligence Model (ATIM)** infrastructure.

Phase 10 provides:
1. **Telemetry Database Persistence (`atim_execution_telemetry` table)**: Immutable PostgreSQL telemetry logs capturing natural language prompts, selected model ID, provider, fallback usage, latencies, token counts, Decimal USD cost expenditure, prompt security audits, and advisory execution decisions.
2. **Real-Time Observability Engine (`ATIMObservabilityService`)**: Real-time aggregation of latency percentiles (P50, P75, P90, P95, P99), provider token/cost breakdowns, and prompt security block rates in tenant isolation.
3. **ATIM Facade Coordinator (`ATIMFacadeService`)**: Pipeline coordinator orchestrating Prompt Security $\rightarrow$ Model Routing $\rightarrow$ Intent/Plan Generation $\rightarrow$ Plan Validation $\rightarrow$ AGENTGUARD/FRAUDGUARD Advisory Check $\rightarrow$ Telemetry Persistence.
4. **Production REST API Controller (`/api/v1/atim/*`)**: FastAPI controller exposing `/analyze`, `/evaluate`, `/models`, `/telemetry`, and `/circuit-breaker/reset` endpoints guarded by JWT authentication and tenant boundary isolation.

---

## Authoritative Security Boundary Architecture

```text
USER / AGENT CLIENT REQUEST
           ↓
=====================================================
ATIM API CONTROLLER (/api/v1/atim/analyze)
           ↓
ATIM PROMPT SECURITY (Phase 4 PromptGuard)
           ↓ [Blocked if Injection / Secret Leak]
TASK & RISK CLASSIFIER (Phase 9 Task/Risk Engine)
           ↓
MODEL ELIGIBILITY FILTER (Floor: 0.95 Security Score)
           ↓
PROVIDER CIRCUIT BREAKER (CLOSED / OPEN / HALF_OPEN)
           ↓
INTELLIGENT ROUTER (Optimal Model / Fallback)
           ↓
LLM PROVIDER / RULE ENGINE
           ↓
STRUCTURED INTENT & DYNAMIC PLAN PROPOSAL (Phase 2 & 3)
           ↓
DETERMINISTIC PLAN VALIDATOR (DAG Cycle & Tool Check)
           ↓
=====================================================
       AUTHORITATIVE SECURITY BOUNDARY
=====================================================
           ↓
       AGENTGUARD (Policy & Velocity Limits)
           ↓
       FRAUDGUARD (ML Risk & XAI Engine)
           ↓
       HUMAN-IN-THE-LOOP (HITL Threshold Check)
           ↓
       RAZORPAY PAYMENT SETTLEMENT
```

> [!IMPORTANT]
> ATIM endpoints return **advisory intelligence proposals** only. ATIM **NEVER** directly authorizes or settles payment orders. Authoritative financial controls remain enforced exclusively by server-side AGENTGUARD, FRAUDGUARD, HITL, and Razorpay integrations.

---

## API Reference

### 1. `POST /api/v1/atim/analyze`
Executes natural language transaction intelligence analysis.
- **Request Body**:
  ```json
  {
    "prompt": "Transfer $100.00 to vendor for hosting services",
    "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "agent_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "requested_action": "payment",
    "requested_amount": 100.00,
    "requested_currency": "USD"
  }
  ```
- **Response**:
  ```json
  {
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "agent_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "prompt_security_blocked": false,
    "selected_model": "openai/gpt-4o",
    "provider": "openai",
    "fallback_used": false,
    "task_type": "INTENT_EXTRACTION",
    "complexity": "MODERATE",
    "risk_level": "MEDIUM",
    "proposed_intent": {
      "action": "payment",
      "amount": "100.00",
      "currency": "USD"
    },
    "plan_valid": true,
    "agentguard_decision": "ALLOWED",
    "fraudguard_score": 0.05,
    "hitl_required": false,
    "final_execution_decision": "ALLOW",
    "latency_ms": 14.50,
    "estimated_cost_usd": "0.001500"
  }
  ```

### 2. `GET /api/v1/atim/telemetry`
Retrieves tenant real-time telemetry metrics and latency percentiles.

### 3. `GET /api/v1/atim/models`
Retrieves registered LLM models, security scores, context limits, and circuit breaker status.

### 4. `POST /api/v1/atim/circuit-breaker/reset`
Resets provider circuit breaker state to `CLOSED`.

---

## Database Schema (`atim_execution_telemetry`)

| Column Name | Data Type | Nullable | Description |
|---|---|---|---|
| `id` | UUID (PK) | No | Unique telemetry record ID |
| `tenant_id` | UUID (Index) | No | Tenant isolation key |
| `agent_id` | UUID (Index) | Yes | Agent ID |
| `request_id` | UUID | Yes | Correlation request ID |
| `prompt_text` | VARCHAR(2048) | Yes | Input prompt text |
| `is_security_blocked` | BOOLEAN | No | True if blocked by PromptGuard |
| `selected_model` | VARCHAR(128) | Yes | Selected LLM model ID |
| `provider` | VARCHAR(64) | Yes | Provider name |
| `latency_ms` | FLOAT | Yes | Execution duration in ms |
| `total_tokens` | INTEGER | Yes | Total tokens consumed |
| `estimated_cost_usd` | NUMERIC(12, 6) | Yes | Estimated cost in Decimal USD |
| `execution_decision` | VARCHAR(64) | Yes | Final execution decision code |
| `created_at` | TIMESTAMPTZ | No | Timestamp |
