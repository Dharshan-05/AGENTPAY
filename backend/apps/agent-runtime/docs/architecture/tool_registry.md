# AGENTPAY Architecture Specification: Phase 157 — Centralized Tool Registry

## Overview
Phase 157 introduces the central Tool Registry subsystem in AGENTPAY, enabling multi-tenant tool registration, versioning, discovery, and lifecycle management.

## Schema & ORM Model
- Table: `tool_definitions`
- Primary Key: UUIDv7
- Indexes: `tenant_id`, `tool_id`, `name`, `category`, `status`, `risk_classification`
- Unique Constraint: `(tenant_id, name, version)`

## Tool Lifecycle States
- `REGISTERED`: Tool registered, pending enablement.
- `ENABLED`: Tool active and executable by authorized agents.
- `DISABLED`: Tool temporarily suspended.
- `DEPRECATED`: Tool flagged for deprecation.
- `REMOVED`: Soft-deleted tool.

## API Endpoints
- `POST /api/v1/tools` (requires `tools:register`)
- `GET /api/v1/tools` (requires `tools:read`)
- `GET /api/v1/tools/{tool_id}` (requires `tools:read`)
- `PATCH /api/v1/tools/{tool_id}` (requires `tools:update`)
- `POST /api/v1/tools/{tool_id}/enable` (requires `tools:enable`)
- `POST /api/v1/tools/{tool_id}/disable` (requires `tools:disable`)
