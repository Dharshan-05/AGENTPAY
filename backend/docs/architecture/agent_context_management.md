# Agent Context Management Architecture (Phase 152)

## Overview
The Agent Context Management subsystem is responsible for deterministic context assembly, prioritization, limiting, truncation, and sanitization for AGENTPAY autonomous payment agents.

## Canonical Scopes & Priority Taxonomy
1. `SYSTEM` (Priority 100): Security posture, system constraints, token budgets.
2. `AGENT_IDENTITY` (Priority 90): Agent slug, type, status, trust score.
3. `USER` (Priority 70): User prompt and user-level preference metadata.
4. `CONVERSATION` / `TASK` (Priority 60): Session UUID, task UUID, active workflow context.
5. `TOOL` (Priority 50): Registered tool capabilities and schema signatures.
6. `RUNTIME` (Priority 40): Operational state parameters and environment flags.

## Context Assembly Pipeline
1. **Tenant Isolation & IDOR Check**: Validates `agent_id` belongs to `tenant_id`.
2. **Secret Sanitization**: Scans and redacts credentials, Bearer tokens, API keys using `SECRET_PATTERN`.
3. **Deduplication & Expiration**: Filters expired items (`expires_at < now`) and deduplicates identical content payloads.
4. **Prioritization & Ordering**: Sorts context items by `priority` (descending), `relevance_score` (descending), and `created_at`.
5. **Token Budgeting & Scope-Preserved Truncation**: Enforces `ContextBudget.max_tokens`. Protected scopes (`SYSTEM`, `AGENT_IDENTITY`) are exempt from budget truncation.
6. **Audit Event Registration**: Emits `context_assembled` audit event.

## REST Endpoints
- `POST /api/v1/agents/{agent_id}/context/assemble` (`agents:context_assemble`)
