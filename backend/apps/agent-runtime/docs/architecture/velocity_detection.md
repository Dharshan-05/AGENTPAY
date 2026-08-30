# Phase 137 — Velocity Detection Architecture

## Purpose
Phase 137 implements activity velocity detection (`AgentVelocityDetectionService`) for AGENTPAY, measuring agent transaction count and monetary volume within configurable bounded time windows (`1h`, `24h`, `7d`).

## Architectural Invariants
- **Bounded Queries**: Employs indexed time-range queries (`created_at >= window_start`) to prevent full database scans.
- **Edge Case Coverage**: Correctly handles zero activity, exact threshold matches, threshold overflow, and overlapping windows.
- **Read/Analysis-Oriented**: Does NOT independently reject payments or suspend agents.
- **Tenant Isolation**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant attempts return `HTTP 404 Not Found` (`AgentNotFoundError`).
- **Integrations**: Threshold overflow emits structured security events (`security_control_triggered`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/velocity` | `agents:velocity_read` | Evaluate agent activity velocity within bounded window |
