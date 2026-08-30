# Phase 139 — Category Behaviour Analysis Architecture

## Purpose
Phase 139 implements category-level behaviour analysis (`AgentCategoryBehaviourService`) for AGENTPAY. It analyzes transaction frequencies, category concentration ratios, and monetary volume distribution across merchant/product categories.

## Architectural Invariants
- **Deterministic & Bounded Metrics**: All transaction and volume ratios are mathematically bounded ($0.00 \le \text{ratio} \le 1.00$). Handles zero activity safely without returning NaN or Infinity.
- **Read-Oriented**: Does NOT mutate agent lifecycle status or execute payments.
- **Tenant Isolation**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant attempts return `HTTP 404 Not Found` (`AgentNotFoundError`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/category-behaviour` | `agents:category_behaviour_read` | Analyze category-level activity distribution for an agent |
