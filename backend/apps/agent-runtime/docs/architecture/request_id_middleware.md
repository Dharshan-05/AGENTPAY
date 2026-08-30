# AGENTPAY Request ID / Correlation ID Architecture

## Overview & Distributed Tracing Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses `RequestIDMiddleware` (`app/middleware/request_id.py`) to establish a unique correlation identity for every incoming HTTP request.

The Request ID serves as the fundamental building block for:
- **Distributed Tracing**: Tracking requests as they flow across microservices and sub-components.
- **Structured Log Correlation**: Binding log records emitted during a single HTTP request lifecycle.
- **Operational Debugging**: Allowing SRE and Support teams to search logs using a single identifier (`request_id`).
- **Incident Investigation**: Bounding error tracebacks, domain exceptions, and API transport metrics to specific client interactions.
- **OpenTelemetry & W3C Trace Context Compatibility**: Designed for seamless mapping to OpenTelemetry `trace_id` in future observability phases.

---

## Header & Validation Specification

- **HTTP Header**: Canonical header `X-Request-ID` (case-insensitive lookup on ingress).
- **Default Generation Strategy**: When the client omits `X-Request-ID`, the middleware generates a fresh UUID4 (`str(uuid.uuid4())`).
- **Validation Rules**:
  - Maximum Length: 128 characters.
  - Allowed Characters: `A-Z`, `a-z`, `0-9`, `-`, `_`, `.`.
  - Rejection Policy: Control characters (`\r`, `\n`, `\t`), spaces, quotes, HTML/script tags, and header injection payloads are rejected with `HTTP 400 Bad Request` (`VALIDATION_ERROR`, `"Invalid request ID."`).
  - Zero Echo Guarantee: Malicious or invalid request ID values are never echoed back in HTTP error response bodies or headers.

---

## Request State & Lifecycle Flow

```text
HTTP Request → RequestIDMiddleware → APIMiddleware → CORSMiddleware → ExceptionMiddleware → Router → Application → Domain
```

1. **Ingress & Validation**: `RequestIDMiddleware` validates or generates the `X-Request-ID` and attaches it to `request.state.request_id`.
2. **Context Propagation**: `request.state.request_id` is available to all downstream middleware, FastAPI dependencies, route controllers, and loggers.
3. **Structured Log Correlation**: `APIMiddleware` (`event="http.request"`) and `ExceptionMiddleware` (`event="application.error"`) include `"request_id": request_id` in single-line JSON log events.
4. **Egress Propagation**: `X-Request-ID: <request_id>` is attached to all outgoing HTTP responses (200, 400, 404, 405, 500, 503).
5. **CORS Exposure**: `CORSMiddleware` exposes `X-Request-ID` in `Access-Control-Expose-Headers` so browser clients can read correlation IDs safely.

---

## Operational Log Search Example

```json
{
  "timestamp": "2026-08-25T15:30:00Z",
  "level": "INFO",
  "logger": "agentpay.middleware.api",
  "message": "HTTP request completed",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0",
  "event": "http.request",
  "request_id": "7f5e9d2b-2d43-4f5f-9e89-1e6c3f5a7b21",
  "method": "GET",
  "path": "/api/v1/resource",
  "status_code": 200,
  "duration_ms": 3.45
}
```

Searching logs for `request_id="7f5e9d2b-2d43-4f5f-9e89-1e6c3f5a7b21"` isolates the complete lifecycle of that specific request across log files.

---

## Layer Isolation & Security

- **Framework Isolation**: Domain, application, and infrastructure layers retain zero dependencies on `RequestIDMiddleware`, FastAPI `Request`/`Response`, or HTTP headers.
- **No Global Mutable State**: Request IDs are scoped to the individual `Request.state` object. No thread-local storage or global mutable dictionaries are used.
