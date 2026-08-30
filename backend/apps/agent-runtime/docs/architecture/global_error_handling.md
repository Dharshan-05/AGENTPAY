# AGENTPAY Global Error Handling Architecture

## Overview & Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses a production-grade, layered exception architecture. Application failures are classified into explicit domain, application, infrastructure, and configuration exception hierarchies with stable, machine-readable error codes.

```text
                           AgentPayError
                                 │
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
    DomainError  ApplicationError InfrastructureError ConfigurationError
         │               │               │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    ▼         ▼     ▼         ▼     ▼         ▼
  Entity  Business UseCase Application Database External
Not Found Violation Error Conflict    Error    Service
  (404)    (400)    (500)   (409)     (500)    (503)
```

---

## Machine-Readable Error Codes (`ErrorCode`)

| Error Code | Layer Origin | Description | Target HTTP Mapping (Phase 019) |
| :--- | :--- | :--- | :--- |
| `INTERNAL_ERROR` | Base | Fallback internal application error | `500 Internal Server Error` |
| `INVALID_CONFIGURATION` | Core | Missing or invalid application settings | `500 Internal Server Error` |
| `RESOURCE_NOT_FOUND` | Domain / App | Requested domain entity or resource does not exist | `404 Not Found` |
| `RESOURCE_CONFLICT` | App | Conflict during operation (e.g. duplicate key) | `409 Conflict` |
| `VALIDATION_ERROR` | Schema / API | Request payload parameter validation failure | `400 Bad Request` |
| `DOMAIN_ERROR` | Domain | Domain invariant or business rule violation | `400 Bad Request` |
| `APPLICATION_ERROR` | Application | Application use-case execution failure | `500 Internal Server Error` |
| `INFRASTRUCTURE_ERROR` | Infrastructure | Database ORM or caching adapter failure | `500 Internal Server Error` |
| `SERVICE_UNAVAILABLE` | Infrastructure | External integration API or gateway timeout | `503 Service Unavailable` |

---

## Key Architecture Principles

1. **Public vs Internal Separation**: Public error messages (`str(err)`) contain only safe, user-friendly text suitable for API clients. Internal diagnostics (`internal_message`, database hostnames, stack traces) are preserved in internal fields and written to Phase 017 structured JSON logs.
2. **Domain Layer HTTP Decoupling**: Domain exception classes (`app/domain/exceptions/`) have ZERO dependencies on web frameworks (`fastapi`, `starlette`, `HTTPException`). They model domain logic failures rather than HTTP responses.
3. **Application & Infrastructure Decoupling**: Application use cases and infrastructure adapters raise domain/application/infrastructure errors without importing `fastapi.HTTPException`.
4. **Secret Protection**: Exception `details` dictionaries are automatically sanitized using `sanitize_structured_data()`. Sensitive parameter keys (`password`, `secret`, `token`, `api_key`, `authorization`, `bearer`) are masked as `"[REDACTED]"`.
5. **Python Exception Chaining**: Full support for standard exception chaining (`raise NewError(...) from original_exc`), preserving root diagnostic causes.

---

## Future Phase Integration

- **Phase 018 (Current)**: Global Error Handling Foundation (`AgentPayError`, `ErrorCode`, layered exception classes, public/internal message separation, secret redaction, architecture tests).
- **Phase 019**: Exception Middleware & FastAPI exception handlers (translating `AgentPayError` exceptions into standardized HTTP error responses).
- **Phase 025**: Standardized API Response Envelopes.
