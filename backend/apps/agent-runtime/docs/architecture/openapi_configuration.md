# AGENTPAY OpenAPI Configuration Architecture

## Overview & Design Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses a centralized OpenAPI configuration module (`app/core/openapi.py`) to manage API metadata, contact details, tag taxonomies, server descriptions, vendor extensions (`x-service`, `x-api-version`), and cached schema generation.

This centralizes all OpenAPI primitives cleanly at the API/core boundary without leaking framework internals into domain, application, or infrastructure layers.

---

## Centralized OpenAPI Metadata & Primitives

- **Title**: `AGENTPAY API` (derived from `Settings.app_name`)
- **Version**: `1.0.0` (derived from `Settings.app_version`)
- **Description**: Configured in `Settings.description`
- **Contact**: `{"name": "AGENTPAY Platform Engineering"}`
- **Vendor Extensions**:
  - `x-service`: `"agentpay-api"`
  - `x-api-version`: `"1.0.0"`
- **Servers**:
  - Development: `[{"url": "http://localhost:8000", "description": "Local Development Server"}]`

---

## Tag Taxonomy & Operation IDs

| Tag | Description | Operation IDs |
| :--- | :--- | :--- |
| `System` | Core status and root endpoints | `root_check` (`GET /`) |
| `Health` | Process liveness probes | `health_check` (`GET /api/v1/health`) |
| `Readiness` | Traffic readiness probes | `readiness_check` (`GET /api/v1/ready`) |

All operation IDs are globally unique, deterministic, and stable.

---

## Schema Caching & Deterministic Generation

The `configure_openapi(app)` function wraps FastAPI's `get_openapi()` helper and caches the resulting dictionary in `app.openapi_schema`.

- **Determinism**: Repeated calls to `/openapi.json` produce identical, bit-for-bit equivalent output (`schema_1 == schema_2`).
- **Performance**: Zero runtime overhead per request; generated once on first request or application startup.

---

## Production Security & Secret Protection

- **Zero Secret Exposure**: Public `/openapi.json` schemas are scanned by automated unit tests (`tests/unit/test_openapi_configuration.py`) asserting zero raw secrets (`SECRET_KEY`, `JWT_SECRET`, `API_KEY`, `CLIENT_SECRET`, `DATABASE_URL`, `REDIS_URL`, or passwords) leak in responses.
- **Environment Toggles**: Documentation endpoints can be disabled in production by setting `DOCS_ENABLED=False`, `REDOC_ENABLED=False`, and `OPENAPI_ENABLED=False`.
