# Short-Term Working Memory Architecture (Phase 154)

## Overview
Short-Term Working Memory provides session-scoped (`session_id`) and task-scoped (`task_id`) working memory for AGENTPAY payment agents.

## Key Capabilities
- **Transient State Retention**: Stores intermediate agent decisions, temporary variables, active workflow state, and temporary observations.
- **Logical Namespace**: Uses namespace `"short_term_working_memory"` on the common `AgentMemory` persistence layer.
- **Quota & Memory Limit Enforcement**: Enforces a strict quota limit of **max 50 active working variables** per session/task to prevent memory exhaustion (`MemoryQuotaExceededError`).
- **TTL & Expiration**: Defaults to `ttl_seconds = 3600` (1 hour) with automatic cleanup via `purge_expired_memories`.
- **Tenant Isolation**: Isolated by tenant, agent, session, and task. Cross-tenant access is strictly blocked (`AgentNotFoundError`).

## REST API Operations
- `POST /api/v1/agents/{agent_id}/sessions/{session_id}/memory` (`agents:memory_write`)
- `GET /api/v1/agents/{agent_id}/sessions/{session_id}/memory` (`agents:memory_read`)
- `DELETE /api/v1/agents/{agent_id}/sessions/{session_id}/memory` (`agents:memory_delete`)
