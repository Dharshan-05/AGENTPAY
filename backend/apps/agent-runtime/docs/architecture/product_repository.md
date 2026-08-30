# AGENTPAY Architecture Specification: Phase 166 — Product Repository

## Overview
Phase 166 implements the infrastructure data access repository (`ProductRepository`) for Product entities in AGENTPAY.

## Repository Responsibilities
- Pure data access abstraction decoupled from business rules.
- Multi-tenant query enforcement (`WHERE tenant_id = :tenant_id AND deleted_at IS NULL`).
- Keyset pagination ordering: `created_at DESC, id DESC`.
- Methods: `create`, `get_by_id`, `get_by_sku`, `list`, `update`, `archive`, `restore`, `exists`.
