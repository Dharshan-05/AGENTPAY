# AGENTPAY Architecture Specification: Phase 175 — Personalization

## Overview
Phase 175 implements memory-driven personalization (`PersonalizationService`) leveraging existing `AgentMemoryService` infrastructure.

## Personalization Boost & Cold-Start Support
- Recalls agent preference keywords from `AgentMemory` within tenant scope (`tenant_id`, `agent_id`).
- Applies a bounded personalization boost (`0.0` to `0.2`): `final_score = min(1.0, base_rank_score + boost)`.
- Cold-Start Graceful Fallback: If agent memory records are empty or `agent_id` is omitted, `personalization_applied = False` and `boost = 0.0` (returns unboosted ranked candidates).
- Privacy Protection: Zero raw memory records or internal secrets exposed in API contracts.
- **REST Endpoint**: `GET /api/v1/products/personalized?agent_id={id}&query=headphones&limit=10`.
