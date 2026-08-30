# Phase 138 — Merchant Behaviour Analysis Architecture

## Purpose
Phase 138 introduces merchant interaction behaviour analysis (`AgentMerchantBehaviourService`) for AGENTPAY, measuring merchant interaction frequency, top merchant concentration ratio, and new merchant addition rates.

## Architectural Invariants
- **Explainable Analytical Metrics**: Calculates top merchant concentration ratio ($0.00 \le \text{ratio} \le 1.00$) and 7-day new merchant addition rate.
- **Risk Indicators**: `normal`, `unusual_concentration`, `new_merchant_burst`.
- **Read/Analysis-Oriented**: Does NOT modify agent lifecycle state or execute payments.
- **Strict Scope Boundary**: Category Behaviour Analysis (Phase 139) is strictly excluded.
- **Tenant Isolation**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant attempts return `HTTP 404 Not Found` (`AgentNotFoundError`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/merchant-behaviour` | `agents:merchant_behaviour_read` | Analyze merchant interaction patterns for an agent |
