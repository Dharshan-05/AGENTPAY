# AGENTPAY API Middleware Architecture

## Overview & Responsibility

The AGENTPAY backend service (`apps/agent-runtime`) uses a centralized HTTP API Middleware layer (`app/middleware/api.py`). The `APIMiddleware` wraps the FastAPI application stack, observing request processing duration via high-resolution monotonic clocks (`time.perf_counter()`), capturing request method, clean path, and status code, and emitting structured JSON lifecycle log events (`event="http.request"`) via Phase 017 structured logging.

```text
                        HTTP Request
                             │
                             ▼
                      APIMiddleware
                 (app/middleware/api.py)
                    [start_time = perf_counter()]
                             │
                             ▼
                    ExceptionMiddleware
              (app/middleware/exception.py)
                             │
                             ▼
                    FastAPI Router & Endpoint
                             │
                             ▼
                     Response / Error
                             │
                             ▼
                      APIMiddleware
                [duration_ms = (end - start) * 1000]
                [Log: event="http.request"]
                             │
                             ▼
                        HTTP Response
```

---

## Centralized Middleware Pipeline Registration (`app/middleware/registration.py`)

All application middleware is registered centrally in `app/middleware/registration.py` in deterministic pipeline order:

```python
def register_middleware(app: FastAPI) -> None:
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(APIMiddleware)
```

### Pipeline Execution Order
1. Ingress: `APIMiddleware` → `ExceptionMiddleware` → Router → Endpoint Handler.
2. Egress: Endpoint Handler → Router → `ExceptionMiddleware` (converts exceptions to safe JSON responses) → `APIMiddleware` (captures timing and status code) → Client.

---

## Structured Request Log Payload Specification

Every completed HTTP request emits a structured JSON log event containing the following fields:

```json
{
  "timestamp": "2026-08-25T15:40:00Z",
  "level": "INFO",
  "logger": "agentpay.middleware.api",
  "message": "HTTP request completed",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0",
  "event": "http.request",
  "method": "GET",
  "path": "/api/v1",
  "status_code": 200,
  "duration_ms": 4.21
}
```

---

## Strict Privacy & Secret Protection Policy

To protect customer privacy and sensitive credentials:
1. **Query Strings**: Query string parameters (`?token=SECRET`) are NEVER logged. The `path` attribute captures `request.url.path` exclusively.
2. **Request & Response Bodies**: Request payloads (`POST` bodies) and response bodies are NEVER consumed or logged by middleware.
3. **Request Headers**: Sensitive headers (`Authorization`, `Cookie`, `X-API-Key`) are NEVER logged.
4. **Pass-Through Stream Safety**: Middleware does not buffer or intercept ASGI request/response streams.

---

## Layer Isolation Architecture Rules

1. **Middleware Ownership**: Generic HTTP middleware lives strictly in `app/middleware/`.
2. **Zero Layer Dependencies**: Domain (`app/domain/`), application (`app/application/`), and infrastructure (`app/infrastructure/`) layers MUST NOT import `app.middleware`, `FastAPI`, `Starlette`, `Request`, or `Response`.
3. **Exception Boundary Integration**: Downstream exceptions propagate to `ExceptionMiddleware` without being swallowed or double-logged by `APIMiddleware`.

---

## Future Phase Integration

- **Phase 021 (Current)**: Generic API Middleware pipeline, request lifecycle timing, structured logging (`http.request`), secret protection, and exception propagation.
- **Phase 022**: CORS Configuration Middleware.
- **Phase 023**: Request Validation Middleware.
- **Phase 024**: Request ID Middleware (`X-Request-ID` generation & propagation).
- **Phase 025**: Response Standardization Envelopes.
