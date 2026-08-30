# AGENTPAY — Agent Runtime Backend Service

The `agent-runtime` service is the core Python backend service for the AGENTPAY platform, built with FastAPI and clean layered architecture.

## Development & Execution Commands

### Development Server
```bash
py -m uvicorn app.main:app --reload --port 8000
```

### Run Test Suite
```bash
py -m pytest -v
```

### Static Code Quality
```bash
py -m ruff check app tests
py -m mypy app tests
```

## Architecture Summary

This service follows a strict Layered Architecture:
- `app/api/`: HTTP routing and controllers.
- `app/application/`: Use cases, application services, commands, queries, and DTOs.
- `app/domain/`: Framework-independent domain entities, value objects, domain events, repository interfaces, and exceptions.
- `app/infrastructure/`: Database, cache, messaging, persistence, and external service adapters.
- `app/core/`: Application settings configuration, lifespan lifecycle (`lifespan.py`), service bootstrap (`bootstrap.py`), structured logging (`logging.py`), and centralized OpenAPI metadata configuration (`openapi.py`).

- `app/schemas/`: API request/response transport contracts.
- `tests/`: Automated unit, integration, contract, and architecture tests.

## API Documentation

- **Swagger UI**: `/docs` (configurable via `DOCS_ENABLED` / `DOCS_URL`)
- **ReDoc**: `/redoc` (configurable via `REDOC_ENABLED` / `REDOC_URL`)
- **OpenAPI Schema**: `/openapi.json` (configurable via `OPENAPI_ENABLED` / `OPENAPI_URL`)


## Structured Logging Example


```json
{
  "timestamp": "2026-08-25T15:00:00Z",
  "level": "INFO",
  "logger": "agentpay.lifespan",
  "message": "Initializing AGENTPAY application lifecycle...",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0"
}
```

## Exception Middleware HTTP Translation Flow

```text
Application Exception (e.g. EntityNotFoundError)
          ↓
  Exception Middleware (app/middleware/exception.py)
          ↓
  Mapped HTTP Status Code (e.g. 404 Not Found)
          ↓
  Safe Standardized Error JSON Response:
  {
    "success": false,
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Target entity account_123 does not exist.",
      "details": null
    },
    "meta": {
      "request_id": "7f5e9d2b-2d43-4f5f-9e89-1e6c3f5a7b21"
    }
  }
```

## API Versioning

API versioning follows canonical **URL Path Versioning** (`/api/v1`):
- Active API Contract: `/api/v1/...` (derived dynamically from `Settings.api_prefix` and `Settings.api_v1_prefix`).
- Future Extensibility: `/api/v2/...` can be mounted in `app/api/router.py` without modifying domain or application layers.

## API Middleware Pipeline Flow

```text
  HTTP Request Egress / Ingress
                ↓
  RequestIDMiddleware (app/middleware/request_id.py) -> [Validates/generates X-Request-ID]
                ↓
  ResponseStandardizationMiddleware (app/middleware/response.py) -> [Wraps payloads into SuccessResponse]
                ↓
  APIMiddleware (app/middleware/api.py) -> [Measures duration_ms, logs event="http.request"]
                ↓
  CORSMiddleware -> [Validates trusted Origin, exposes X-Request-ID, handles OPTIONS preflight]
                ↓
  Request Validation (Pydantic v2) -> [Rejects extra fields & malformed input]
                ↓
  ExceptionMiddleware (app/middleware/exception.py) -> [Translates exceptions to ErrorResponse]
                ↓
  API Version Router (app/api/router.py -> app/api/v1/router.py)
                ↓
  Application Use Case Layer
                ↓
  Domain Business Layer
```









