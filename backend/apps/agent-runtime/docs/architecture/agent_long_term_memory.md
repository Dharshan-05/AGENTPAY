# AGENTPAY Architecture Specification: Phase 155 — Agent Long-Term Memory Subsystem

## Overview
Phase 155 introduces long-term memory evolution to AGENTPAY, transforming short-term session state into a persistent, multi-tenant knowledge graph for autonomous financial agents.

## Core Components
- **Memory Lifecycle Manager**: Implements lifecycle state transitions: `ACTIVE` -> `STALE` -> `ARCHIVED` -> `DELETED`.
- **Multi-Factor Weighted Recall Engine**: Computes dynamic relevance scores combining:
  1. Importance Weight ($w_1 = 0.35$)
  2. Confidence Score ($w_2 = 0.20$)
  3. Recency Linear Decay ($w_3 = 0.25$, 30-day linear decay)
  4. Search Query / Keyword Relevance ($w_4 = 0.20$)
- **Context Assembly Integration**: Seamlessly injects high-relevance recalled memories into Phase 152 context assembly pipeline.

## API Endpoints
- `POST /api/v1/agents/{agent_id}/memories/{memory_id}/archive` (requires `agents:memory_write`)
- `POST /api/v1/agents/{agent_id}/memories/{memory_id}/restore` (requires `agents:memory_write`)
- `POST /api/v1/agents/{agent_id}/memories/recall` (requires `agents:memory_read`)
