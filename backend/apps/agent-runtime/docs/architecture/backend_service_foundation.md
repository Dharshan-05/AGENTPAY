# AGENTPAY Backend Service Foundation Architecture

## Executive Summary

This document formalizes the consolidated, production-grade backend service foundation (`apps/agent-runtime`) built across PHASES 011–030 of the AGENTPAY platform.

The foundation provides a secure, deterministic, observable, and maintainable Python backend baseline using FastAPI, Starlette, Pydantic v2, and clean layered architecture.

---

## Foundation Architecture & Layer Boundaries

```text
                  HTTP Transport & Client Request (Egress / Ingress)
                                          │
                                          ▼
                      API Router & Controllers (app/api/)
                                          │
                                          ▼
                      Application Use Cases (app/application/)
                                          │
                                          ▼
                      Domain Entities & Rules (app/domain/)
                                          ▲
                                          │
                   Infrastructure Adapters (app/infrastructure/)
```

### Layer Isolation Rules

1. **Domain Layer (`app/domain/`)**: 100% framework-independent; contains zero FastAPI, Starlette, HTTP, middleware, OpenAPI, or secret management dependencies.
2. **Application Layer (`app/application/`)**: Manages use-case logic, DTO contracts, and readiness check registries; free of HTTP responses or transport frameworks.
3. **Infrastructure Layer (`app/infrastructure/`)**: Implements persistence and external service interfaces; contains no API routing logic.
4. **API Layer (`app/api/`)**: Manages HTTP controllers, routing, operation IDs, and response transport models.
5. **Core Layer (`app/core/`)**: Houses configuration (`config.py`), service bootstrap (`bootstrap.py`), lifespan management (`lifespan.py`), logging (`logging.py`), and OpenAPI metadata (`openapi.py`).

---

## Service Bootstrap & Lifecycle Management

- **Application Factory (`create_app()`)**: Located in `app/main.py`, delegates cleanly to `bootstrap_app()` in `app/core/bootstrap.py` for idempotent setup.
- **Service Operational States (`ServiceState`)**:
  - `STARTING`: Application lifecycle initialization in progress.
  - `READY`: Service is healthy and actively receiving production traffic.
  - `STOPPING`: Graceful shutdown initiated; new traffic readiness gated (HTTP 503).
  - `STOPPED`: Process lifecycle completed cleanly.
  - `FAILED`: Startup hook failed; traffic readiness blocked (HTTP 503).
- **Lifecycle Component Protocol (`LifecycleComponent`)**: Extensible protocol (`startup()`, `shutdown()`) for future database, Redis, and messaging adapters.

---

## Middleware Execution Pipeline

1. **RequestIDMiddleware (`app/middleware/request_id.py`)**: Preserves or generates `X-Request-ID` correlation UUID4.
2. **CORSMiddleware (`app/middleware/registration.py`)**: Validates origin allowlist, exposes correlation headers, handles OPTIONS preflights.
3. **APIMiddleware (`app/middleware/api.py`)**: Measures `duration_ms` using monotonic timers, emits structured `http.request` JSON logs.
4. **ExceptionMiddleware (`app/middleware/exception.py`)**: Intercepts unhandled application errors and maps to safe `ErrorResponse` HTTP payloads.
5. **ResponseStandardizationMiddleware (`app/middleware/response.py`)**: Wraps successful controller returns into `SuccessResponse[T]`.

---

## Traffic Readiness vs. Process Liveness

| Endpoint | Purpose | Ready Response | Failure Response |
| :--- | :--- | :--- | :--- |
| `GET /api/v1/health` | Process Liveness Probe | `200 OK` (`{"status": "healthy"}`) | - |
| `GET /api/v1/ready` | Traffic Readiness Probe | `200 OK` (`{"status": "ready"}`) | `503 Service Unavailable` |

---

## Production Security & Secret Hardening

- **Zero Secret Exposure**: Public OpenAPI schemas, HTTP response envelopes, and structured log events are verified by automated tests to contain zero raw secret values (`SECRET_KEY`, `JWT_SECRET`, `API_KEY`, `CLIENT_SECRET`, `DATABASE_URL`, `REDIS_URL`).
- **Environment Constraints**: `DEBUG=True` and wildcard CORS (`*`) are strictly forbidden in production (`app_env="production"`).
