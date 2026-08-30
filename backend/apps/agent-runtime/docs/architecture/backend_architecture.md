# AGENTPAY Backend Layered Architecture

## Architectural Philosophy & Layered Boundaries

The AGENTPAY backend service (`apps/agent-runtime`) uses a Domain-Driven, Layered Architecture designed for high reliability, maintainability, and testability.

```text
               +-----------------------+
               |       API Layer       |
               +-----------------------+
                           |
                           v
               +-----------------------+
               |   Application Layer   |
               +-----------------------+
                           |
                           v
               +-----------------------+
               |     Domain Layer      |
               +-----------------------+
                           ^
                           |
               +-----------------------+
               | Infrastructure Layer  |
               +-----------------------+
```

---

## Architectural Layers

### 1. API Layer (`app/api/`)
- **Responsibilities**: HTTP routing, request parsing, response serialization, API transport schemas, and FastAPI dependencies.
- **Rules**: Must NOT contain business logic or direct persistence queries. Delegates command/query execution to the Application layer.

### 2. Application Layer (`app/application/`)
- **Responsibilities**: Application use cases, command/query orchestration, application services, and Data Transfer Objects (DTOs).
- **Rules**: Must remain HTTP-framework independent (zero imports of FastAPI, Starlette, or HTTP transport code).

### 3. Domain Layer (`app/domain/`)
- **Responsibilities**: Pure business logic, entities, value objects, domain services, domain events, repository interfaces, and domain exceptions.
- **Rules**: Completely framework-independent and infrastructure-agnostic. Must NEVER import FastAPI, Pydantic settings, SQLAlchemy, Redis, or Infrastructure modules.

### 4. Infrastructure Layer (`app/infrastructure/`)
- **Responsibilities**: Concrete implementations of database ORMs, repository persistence, caching, external API clients, message brokers, and observability adapters.
- **Rules**: Implements repository interfaces declared in the Domain layer via Dependency Inversion.

### 5. Core Layer (`app/core/`)
- **Responsibilities**: Cross-cutting application infrastructure including settings configuration (`config.py`) and FastAPI application lifespan management (`lifespan.py`).

### 6. Schemas Layer (`app/schemas/`)
- **Responsibilities**: Standardized response envelopes (`common.py`) and structured error payload contracts (`errors.py`).

---

## Configuration Architecture (`app/core/config.py`)

- **Single Entry Point**: Access to configuration is controlled exclusively via `get_settings()`, which returns a `@lru_cache`-cached `Settings` singleton instance.
- **Controlled Types**: Environment classifications (`Environment` enum: `development`, `test`, `staging`, `production`, `local`) and log levels (`LogLevel` enum: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) enforce valid inputs.
- **Type Safety & Environment Parsing**: All fields use Pydantic v2 / Pydantic Settings for strict typing, integer port boundaries, and automatic environment variable parsing.
- **Production Safety**: Post-init validation prohibits running `DEBUG=true` in `production` environment, throwing a runtime validation error at startup.
- **Zero Side-Effects**: Configuration loading performs no database queries, network requests, or file-writing side effects.
- **Environment Management**: Detailed environment semantics, convenience API properties (`is_production`, `is_local`), precedence rules, and container runtime injection guidelines are documented in [environment_management.md](environment_management.md).
- **Secrets Configuration**: Sensitive parameters (`SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `API_KEY`, `CLIENT_SECRET`) use `pydantic.SecretStr` for automatic value redaction, length validation, and zero-leakage `safe_summary` diagnostics. Documented in [secrets_configuration.md](secrets_configuration.md).
- **Logging Infrastructure**: Centralized, container-native Python `logging` foundation (`app/core/logging.py`) with ISO-8601 UTC timestamps, stdout stream handling, Uvicorn sync, and secret redaction filters. Documented in [logging_infrastructure.md](logging_infrastructure.md).
- **Structured Logging**: Single-line JSON log event formatter (`JSONFormatter`) producing machine-readable events with required base fields, service identity metadata, event classification, exception payloads, and recursive nested secret redaction. Documented in [structured_logging.md](structured_logging.md).
- **Global Error Handling**: Layered exception hierarchy (`AgentPayError`, `ErrorCode`, domain/application/infrastructure exceptions) with public/internal message separation, secret redaction, and HTTP framework decoupling. Documented in [global_error_handling.md](global_error_handling.md).
- **Exception Middleware**: Central HTTP translation boundary (`app/middleware/exception.py`) mapping `ErrorCode` values to HTTP status codes (404, 409, 400, 500, 503), outputting standardized safe JSON responses, logging structured error records, and insulating internal causes from clients. Documented in [exception_middleware.md](exception_middleware.md).
- **API Versioning**: Production-grade URL path versioning architecture (`/api/v1`) using dynamic configuration prefixes (`Settings.api_prefix` + `Settings.api_v1_prefix`), version ownership in `app/api/`, unknown version 404 safety, layer isolation, and OpenAPI compatibility. Documented in [api_versioning.md](api_versioning.md).
- **API Middleware**: Generic HTTP lifecycle middleware (`app/middleware/api.py`) measuring request duration via high-resolution monotonic timers (`time.perf_counter()`), recording HTTP method, path, and status code, emitting structured JSON events (`event="http.request"`), and enforcing zero secret leakage. Documented in [api_middleware.md](api_middleware.md).
- **CORS Configuration**: Enterprise cross-origin resource sharing architecture (`app/middleware/registration.py`) with environment-driven settings (`Settings.cors_allowed_origins`), explicit method/header allowlists, preflight OPTIONS handling, and production wildcard fail-fast validation. Documented in [cors_configuration.md](cors_configuration.md).
- **Request Validation**: Transport input validation boundary (`app/schemas/requests.py`) using Pydantic v2 strict schemas (`extra="forbid"`), field constraints, zero-secret-leakage exception normalization (`validation_exception_handler`), and HTTP 400 `VALIDATION_ERROR` responses. Documented in [request_validation.md](request_validation.md).
- **Request ID Middleware**: Enterprise request correlation identity architecture (`app/middleware/request_id.py`) validating/generating `X-Request-ID` headers, storing correlation IDs in `request.state.request_id`, attaching correlation IDs to all response headers, and binding log events. Documented in [request_id_middleware.md](request_id_middleware.md).
- **Response Standardization**: Canonical HTTP response architecture (`app/schemas/common.py`, `app/schemas/errors.py`, `app/middleware/response.py`) providing structured `SuccessResponse` and `ErrorResponse` contracts with `meta.request_id` correlation, 204 bodyless preservation, and double-wrapping prevention. Documented in [response_standardization.md](response_standardization.md).
- **API Health Endpoint**: Process liveness health check architecture (`app/api/v1/health.py`) providing lightweight, dependency-free process liveness verification (`GET /api/v1/health`) for Kubernetes, Docker, and load balancers. Documented in [health_endpoint.md](health_endpoint.md).
- **API Readiness Endpoint**: Traffic readiness architecture (`app/api/v1/ready.py`, `app/application/services/readiness.py`) providing fail-closed, extensible readiness evaluation (`GET /api/v1/ready`) returning HTTP 200 (Ready) or HTTP 503 (Not Ready) for load balancer traffic gating. Documented in [readiness_endpoint.md](readiness_endpoint.md).
- **API Documentation**: Enterprise OpenAPI specification, Swagger UI (`/docs`), and ReDoc (`/redoc`) architecture (`app/main.py`, `app/schemas/common.py`, `app/schemas/errors.py`) with environment toggles and zero-secret disclosure safeguards. Documented in [api_documentation.md](api_documentation.md).
- **OpenAPI Configuration**: Centralized OpenAPI metadata, contact info, tag taxonomy, server list, vendor extensions (`x-service`, `x-api-version`), and cached deterministic schema builder (`app/core/openapi.py`). Documented in [openapi_configuration.md](openapi_configuration.md).
- **Backend Service Foundation**: Consolidated service bootstrap architecture, application factory, lifespan state tracking (`ServiceState`), lifecycle component hooks, and production readiness validation (`app/core/bootstrap.py`, `app/core/lifespan.py`). Documented in [backend_service_foundation.md](backend_service_foundation.md).
- **Database Architecture & Strategy (Phase 011)**: PostgreSQL technology decision, domain ownership boundaries, transaction strategy, data integrity rules, UUIDv7 strategy, soft-delete, audit trails, and multi-tenancy rules. Documented in [database_architecture.md](database_architecture.md).
- **PostgreSQL Development Environment (Phase 012)**: Containerized PostgreSQL 15+ stack (`docker-compose.yml`), persistent storage (`postgres_data`), environment variables, health checks (`pg_isready`), and developer reset workflows. Documented in [postgresql_development_environment.md](postgresql_development_environment.md).
- **Database Configuration & Async Engine (Phase 013 + Phase 014)**: Centralized database settings validation (`app/core/config.py`), driver scheme normalization, SQLAlchemy 2.0 AsyncEngine singleton (`app/infrastructure/database/engine.py`), AsyncSession dependency (`app/infrastructure/database/session.py`), SELECT 1 health probe, and lifespan teardown. Documented in [database_configuration_and_engine.md](database_configuration_and_engine.md).
- **Database Connection Pooling & Lifecycle (Phase 015)**: Connection pool parameters (`db_pool_size`, `db_max_overflow`), connection acquisition/release invariants, timeout exhaustion resilience, `get_pool_status` observability, and lifespan disposal. Documented in [database_pooling_and_lifecycle.md](database_pooling_and_lifecycle.md).
- **Database Environment Management (Phase 016)**: Environment classification matrix (Dev, Test, Staging, Prod), test database safety guards, production default password & localhost blocking, and secret isolation. Documented in [database_environment_management.md](database_environment_management.md).
- **Database Migration Framework (Phase 017)**: Alembic async migration pipeline (`alembic/env.py`, `alembic.ini`), dynamic settings integration (`effective_database_url`), test safety guards, and CLI workflow commands. Documented in [database_migration_framework.md](database_migration_framework.md).
- **Migration Versioning Strategy (Phase 018)**: Revision identification standards, linear single-head invariant, revision graph verification (`verify_migration_graph`), downgrade policies, and immutability rules. Documented in [database_migration_versioning.md](database_migration_versioning.md).
- **Database Naming Conventions (Phase 019)**: Lowercase snake_case identifier rules, MetaData naming convention dictionary (`pk_`, `fk_`, `uq_`, `ck_`, `ix_`), reserved word protection, and machine-validatable standards. Documented in [database_naming_conventions.md](database_naming_conventions.md).
- **Database Schema Standards (Phase 020)**: Primary key standards (UUIDv7 `id`), multi-tenancy (`tenant_id`), UTC timezone-aware timestamps (`TIMESTAMPTZ`), exact monetary precision (`NUMERIC`), soft deletion, and foreign key delete policies. Documented in [database_schema_standards.md](database_schema_standards.md).
- **Users Schema (Phase 021)**: Identity table (`users`) with UUIDv7 `id`, tenant isolation (`tenant_id`), tenant-scoped email uniqueness (`uq_users_tenant_id_email`), account status, security tracking, and audit timestamps. Documented in [identity_users_schema.md](identity_users_schema.md).
- **User Profiles Schema (Phase 022)**: User profiles table (`user_profiles`) with foreign key (`fk_user_profiles_user_id_users` `ON DELETE RESTRICT`), one-to-one uniqueness (`uq_user_profiles_user_id`), tenant isolation, and profile metadata. Documented in [user_profiles_schema.md](user_profiles_schema.md).
- **Roles Schema (Phase 023)**: Authorization roles table (`roles`) with tenant-scoped uniqueness (`uq_roles_tenant_id_name`), system role support (`is_system`), status tracking, and soft deletion. Documented in [roles_schema.md](roles_schema.md).
- **Permissions Schema (Phase 024)**: Atomic platform capability permissions table (`permissions`) with global unique permission names (`uq_permissions_name`), resource & action domains, and system flags. Documented in [permissions_schema.md](permissions_schema.md).
- **Role-Permission Schema (Phase 025)**: Normalized junction table (`role_permissions`) mapping tenant-scoped roles to global permissions with unique constraint `uq_role_permissions_role_id_permission_id` and `ON DELETE RESTRICT` FKs. Documented in [role_permission_schema.md](role_permission_schema.md).
- **User-Role Schema (Phase 026)**: Normalized junction table (`user_roles`) mapping users to roles with tenant isolation (`tenant_id`), unique constraint `uq_user_roles_user_id_role_id`, and `ON DELETE RESTRICT` FKs. Documented in [user_role_schema.md](user_role_schema.md).
- **Sessions Schema (Phase 027)**: Authentication session table (`sessions`) with tenant isolation (`tenant_id`), user reference (`fk_sessions_user_id_users`), device metadata, and expiration boundaries. Documented in [sessions_schema.md](sessions_schema.md).
- **Refresh Tokens Schema (Phase 028)**: Cryptographic refresh token registry table (`refresh_tokens`) with mandatory cryptographic digest (`token_hash`), rotation family tracking, revocation state, and zero raw token storage. Documented in [refresh_tokens_schema.md](refresh_tokens_schema.md).
- **Authentication Security Schema (Phase 029)**: User authentication security state table (`authentication_security`) tracking failed login attempts (`ck_authentication_security_failed_login_attempts_nonnegative`), lockout timestamps, and password metadata with 1-to-1 user uniqueness. Documented in [authentication_security_schema.md](authentication_security_schema.md).
- **Login & Security Events Schema (Phase 030)**: Immutable append-only audit event log table (`login_security_events`) tracking authentication events, request contexts, and JSONB metadata with zero secrets. Documented in [login_security_events_schema.md](login_security_events_schema.md).
- **Agents Schema (Phase 031)**: First-class autonomous agent principal table (`agents`) with tenant isolation (`tenant_id`), unique tenant-scoped slug (`uq_agents_tenant_id_slug`), agent type classification, and status tracking. Documented in [agents_schema.md](agents_schema.md).
- **Agent Identity Schema (Phase 032)**: Agent identity profile table (`agent_identities`) with 1-to-1 agent uniqueness (`uq_agent_identities_agent_id`), tenant isolation (`tenant_id`), external reference tracking, and zero credentials. Documented in [agent_identity_schema.md](agent_identity_schema.md).
- **Agent Credentials Schema (Phase 033)**: Agent credential verification table (`agent_credentials`) storing one-way cryptographic verification hashes (`secret_hash`), non-secret lookup IDs (`credential_identifier`), and status lifecycle state with zero plaintext secrets. Documented in [agent_credentials_schema.md](agent_credentials_schema.md).
- **Agent Sessions Schema (Phase 034)**: Agent session context table (`agent_sessions`) tracking active/historical Agent runtime session boundaries, device/IP context, expiration, and JSONB metadata payload with zero raw tokens. Documented in [agent_sessions_schema.md](agent_sessions_schema.md).
- **Agent Permissions Schema (Phase 035)**: Agent permission assignment table (`agent_permissions`) providing direct permission assignments to Agents with tenant isolation (`tenant_id`), unique constraint `uq_agent_permissions_agent_id_permission_id`, and `ON DELETE RESTRICT` FKs. Documented in [agent_permissions_schema.md](agent_permissions_schema.md).
- **Agent Roles Schema (Phase 036)**: Agent role assignment table (`agent_roles`) providing role assignments to Agents with tenant isolation (`tenant_id`), unique constraint `uq_agent_roles_agent_id_role_id`, and `ON DELETE RESTRICT` FKs. Documented in [agent_roles_schema.md](agent_roles_schema.md).
- **Agent Lifecycle Schema (Phase 037)**: Agent operational lifecycle table (`agent_lifecycle`) maintaining current operational state, transition timestamps, reason codes, 1-to-1 agent uniqueness (`uq_agent_lifecycle_agent_id`), and tenant isolation (`tenant_id`). Documented in [agent_lifecycle_schema.md](agent_lifecycle_schema.md).
- **Agent Metadata Schema (Phase 038)**: Agent configuration metadata table (`agent_metadata`) providing non-sensitive extensible JSONB payload (`metadata_payload`), 1-to-1 agent uniqueness (`uq_agent_metadata_agent_id`), tenant isolation (`tenant_id`), and zero secrets. Documented in [agent_metadata_schema.md](agent_metadata_schema.md).
- **Agent Trust Schema (Phase 039)**: Agent security posture and trust evaluation table (`agent_trust`) maintaining trust status (`trust_status`), score rating (`trust_score`), evaluation metadata, 1-to-1 agent uniqueness (`uq_agent_trust_agent_id`), and tenant isolation (`tenant_id`). Documented in [agent_trust_schema.md](agent_trust_schema.md).
- **Agent Audit Schema (Phase 040)**: Immutable append-only agent audit table (`agent_audit`) tracking security-relevant events, actor information, request context, event metadata, tenant isolation (`tenant_id`), and `ON DELETE RESTRICT` FKs with zero `updated_at`/`deleted_at`. Documented in [agent_audit_schema.md](agent_audit_schema.md).
- **Merchants Schema (Phase 041)**: Commercial merchant entity table (`merchants`) maintaining merchant display identity, tenant-scoped unique slug (`uq_merchants_tenant_id_slug`), operational status, soft delete (`deleted_at`), and tenant isolation (`tenant_id`). Documented in [merchant_schema.md](merchant_schema.md).
- **Products Schema (Phase 042)**: Commercial product item table (`products`) maintaining merchant relationship (`ON DELETE RESTRICT`), merchant-scoped unique SKU (`uq_products_merchant_id_sku`), financial precision pricing (`NUMERIC(12,2)`), check constraint `ck_products_price_nonnegative`, currency code, metadata payload, soft delete (`deleted_at`), and tenant isolation (`tenant_id`). Documented in [product_schema.md](product_schema.md).
- **Product Categories Schema (Phase 043)**: Commercial product category table (`product_categories`) supporting self-referencing category hierarchies (`parent_category_id`), tenant/merchant-scoped unique slug (`uq_product_categories_tenant_id_merchant_id_slug`), check constraint `ck_product_categories_no_self_parent`, metadata payload, soft delete (`deleted_at`), and tenant isolation (`tenant_id`). Documented in [database_product_categories_and_inventory.md](database_product_categories_and_inventory.md).
- **Inventory Schema (Phase 044)**: Product inventory table (`inventory`) maintaining stock quantities (`NUMERIC(12,3)`), reserved quantities, check constraints (`quantity >= 0`, `reserved_quantity >= 0`, `reserved_quantity <= quantity`), reorder thresholds, location code, metadata payload, soft delete (`deleted_at`), product-unique constraint (`uq_inventory_tenant_id_product_id`), and tenant isolation (`tenant_id`). Documented in [database_product_categories_and_inventory.md](database_product_categories_and_inventory.md).



































---

## Quality Policies

- **No `utils/` Dumping Ground Policy**: Generic helper modules like `utils.py` are strictly prohibited. Helpers must live beside the specific domain or infrastructure abstraction they serve.
- **Framework Isolation**: Core domain logic is decoupled from FastAPI and database choices to allow independent unit testing without external dependencies.
