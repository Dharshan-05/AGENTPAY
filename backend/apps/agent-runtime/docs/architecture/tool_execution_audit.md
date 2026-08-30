# AGENTPAY Architecture Specification: Phase 159 — Tool Execution Audit Subsystem

## Overview
Phase 159 introduces an append-only, immutable audit trail capturing 100% of tool execution attempts in AGENTPAY.

## Telemetry Schema
- Table: `tool_execution_audits`
- Primary Key: UUIDv7
- Key Fields: `id`, `tenant_id`, `agent_id`, `user_id`, `execution_id`, `request_id`, `correlation_id`, `tool_id`, `tool_version`, `permission_decision`, `approval_state`, `execution_state`, `risk_classification`, `duration_ms`, `error_code`, `environment`, `payload_metadata`, `created_at`.

## Sensitive Data Protection
All payload metadata is automatically processed through `_sanitize_tool_metadata`, redacting keys like `password`, `access_token`, `refresh_token`, `api_key`, `jwt`, `private_key`, `authorization`, `card_number`, `cvv`.
