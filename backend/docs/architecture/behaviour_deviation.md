# Phase 136 — Behaviour Deviation Architecture

## Purpose
Phase 136 implements a production-grade Agent Behaviour Deviation analysis layer (`AgentBehaviourDeviationService`) for AGENTPAY. It evaluates recent agent event frequency against a historical 30-day baseline to calculate explainable deviation metrics.

## Architectural Invariants
- **Deterministic Evaluation**: Uses baseline daily frequency comparisons ($0.00 \le \text{deviation\_score} \le 100.00$) without ML models.
- **Read/Analysis-Oriented**: Does NOT mutate agent lifecycle status or revoke credentials directly.
- **Tenant Isolation**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant attempts return `HTTP 404 Not Found` (`AgentNotFoundError`).
- **Integrations**: High severity deviations automatically generate structured audit log entries (`behaviour_deviation_detected`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/behaviour/deviation` | `agents:behaviour_read` | Evaluate agent behaviour deviation against baseline |
