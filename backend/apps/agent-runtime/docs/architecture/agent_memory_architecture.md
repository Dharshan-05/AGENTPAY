# Unified Agent Memory Architecture (Phase 153)

## Overview
The Unified Agent Memory subsystem provides a common memory abstraction and persistence framework for AGENTPAY agents (`AgentMemory` ORM model, `agent_memories` database table).

## Database Schema & ORM Model
- **Table**: `agent_memories`
- **Migration**: `038_agent_memories.py` (Previous head: `037_user_preferences`)
- **Key Columns**:
  - `id`: UUID (Primary Key)
  - `tenant_id`: UUID (Tenant Isolation Key)
  - `agent_id`: UUID (Agent Principal Key)
  - `session_id`: UUID | None (Active Session Key)
  - `task_id`: UUID | None (Active Task Key)
  - `memory_type`: String ("short_term", "long_term")
  - `namespace`: String (Logical namespace, default `"default"`)
  - `key`: String (Lookup key)
  - `value`: JSONB (Structured payload)
  - `importance`: Float (0.0 to 1.0)
  - `confidence`: Float (0.0 to 1.0)
  - `version`: Integer (Optimistic version counter)
  - `expires_at`: DateTime (TTL expiration timestamp)
- **Unique Constraint**: `uq_agent_memories_tenant_agent_namespace_key`

## Unified Memory API Operations
- `POST /api/v1/agents/{agent_id}/memories` (`agents:memory_write`)
- `GET /api/v1/agents/{agent_id}/memories` (`agents:memory_read`)
- `GET /api/v1/agents/{agent_id}/memories/{memory_id}` (`agents:memory_read`)
- `PATCH /api/v1/agents/{agent_id}/memories/{memory_id}` (`agents:memory_write`)
- `DELETE /api/v1/agents/{agent_id}/memories/{memory_id}` (`agents:memory_delete`)
