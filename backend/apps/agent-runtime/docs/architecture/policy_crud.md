# AGENTGUARD Architecture Specification: Phase 186 — Policy CRUD

## Overview
Phase 186 implements `PolicyService` and `policies_router`, providing complete, tenant-isolated CRUD operations for Security Policies.

## CRUD & Lifecycle Operations
- **CREATE** (`POST /api/v1/policies`): Validates uniqueness of policy `slug` within tenant (`uq_security_policies_tenant_id_slug`). Initializes status to `draft` and version to `1`. Requires `policies:create`.
- **READ** (`GET /api/v1/policies`, `GET /api/v1/policies/{policy_id}`): Lists or gets policy within tenant boundary. Supports status/type filtering and pagination. Requires `policies:read`.
- **UPDATE** (`PATCH /api/v1/policies/{policy_id}`): Updates mutable fields and increments `version += 1`. Requires `policies:update`.
- **ACTIVATION & DEACTIVATION** (`POST /api/v1/policies/{policy_id}/activate`, `POST /api/v1/policies/{policy_id}/deactivate`): Changes status to `active` or `inactive` and increments `version += 1`. Requires `policies:activate` / `policies:deactivate`.
- **ARCHIVE** (`POST /api/v1/policies/{policy_id}/archive`): Soft-deletes policy (`status = "archived"`, `deleted_at = datetime.now(UTC)`). Requires `policies:archive`.

## Permissions Integration
Reuses central permission registry with permissions: `policies:read`, `policies:create`, `policies:update`, `policies:activate`, `policies:deactivate`, `policies:archive`.
