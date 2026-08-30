# AGENTPAY API Documentation Architecture

## Overview & Design Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses FastAPI's native OpenAPI engine to generate an enterprise-grade, machine-readable API specification (`/openapi.json`), interactive Swagger UI (`/docs`), and ReDoc documentation (`/redoc`).

The OpenAPI specification is derived dynamically from application code and Pydantic schemas, serving as the single source of truth for SDK generators, integration partners, frontend clients, and API governance.

---

## Documentation Endpoints & Access Control

| Endpoint | Format | Description | Config Toggle |
| :--- | :--- | :--- | :--- |
| `GET /openapi.json` | JSON (OpenAPI 3.1.0) | Machine-readable OpenAPI specification | `OPENAPI_ENABLED` |
| `GET /docs` | HTML (Swagger UI) | Interactive API exploration and testing interface | `DOCS_ENABLED` |
| `GET /redoc` | HTML (ReDoc) | Responsive API reference documentation | `REDOC_ENABLED` |

---

## API Metadata & Tag Hierarchy

- **Title**: `AGENTPAY API` (derived from `Settings.app_name`)
- **Version**: `1.0.0` (derived from `Settings.app_version`)
- **Description**: Configured in `Settings.description`

### Tag Taxonomy

1. **System**: Core platform status and root endpoints (`GET /`).
2. **Health**: Process liveness probes for container lifecycle management (`GET /api/v1/health`).
3. **Readiness**: Traffic readiness probes for load balancing and service discovery (`GET /api/v1/ready`).

---

## Canonical Schema Bindings

OpenAPI components accurately declare the canonical response envelopes:

- **Success Envelope (`SuccessResponse[T]`)**:
  ```json
  {
    "success": true,
    "data": { ... },
    "meta": {
      "request_id": "<request-id>"
    }
  }
  ```
- **Error Envelope (`ErrorResponse`)**:
  ```json
  {
    "success": false,
    "error": {
      "code": "SERVICE_UNAVAILABLE",
      "message": "Service is not ready.",
      "details": null
    },
    "meta": {
      "request_id": "<request-id>"
    }
  }
  ```

---

## Production Security & Secret Safeguards

- **Zero Secret Disclosure**: `SecretStr` fields, environment credentials, database URLs, Redis URLs, JWT secrets, and API keys are strictly excluded from generated OpenAPI schemas and examples.
- **Environment Toggles**: Documentation endpoints can be disabled in production or staging by configuring `DOCS_ENABLED=False`, `REDOC_ENABLED=False`, and `OPENAPI_ENABLED=False`.
- **Deterministic Schema Output**: The OpenAPI schema generation is deterministic and contains no dynamic timestamps or request-specific random values.
