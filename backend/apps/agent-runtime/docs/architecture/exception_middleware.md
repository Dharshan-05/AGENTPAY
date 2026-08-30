# AGENTPAY Exception Middleware Architecture

## Overview & Responsibility

The AGENTPAY backend service (`apps/agent-runtime`) uses an Exception Middleware HTTP translation layer (`app/middleware/exception.py`). It catches application exceptions (`AgentPayError`) and unhandled system failures (`Exception`), converting them into safe, standardized HTTP JSON responses while maintaining strict layer isolation between domain/application logic and HTTP transport contracts.

```text
       Domain / Application / Infrastructure
                         │
                         ▼
                   AgentPayError
                         │
                         ▼
               Exception Middleware
           (app/middleware/exception.py)
                         │
       ┌─────────────────┴─────────────────┐
       ▼                                   ▼
 Structured JSON                      Safe Public
   Log Event                         HTTP Response
 (stdout stream)                  (application/json)
```

---

## Error Code to HTTP Status Code Mapping Matrix

| Error Code | Layer Origin | Target HTTP Status | Response `code` Field |
| :--- | :--- | :--- | :--- |
| `RESOURCE_NOT_FOUND` | Domain / App | `404 Not Found` | `"RESOURCE_NOT_FOUND"` |
| `RESOURCE_CONFLICT` | App | `409 Conflict` | `"RESOURCE_CONFLICT"` |
| `VALIDATION_ERROR` | Schema / API | `400 Bad Request` | `"VALIDATION_ERROR"` |
| `DOMAIN_ERROR` | Domain | `400 Bad Request` | `"DOMAIN_ERROR"` |
| `APPLICATION_ERROR` | Application | `400 Bad Request` | `"APPLICATION_ERROR"` |
| `INVALID_CONFIGURATION` | Core | `500 Internal Server Error` | `"INVALID_CONFIGURATION"` |
| `INFRASTRUCTURE_ERROR` | Infrastructure | `500 Internal Server Error` | `"INFRASTRUCTURE_ERROR"` |
| `SERVICE_UNAVAILABLE` | Infrastructure | `503 Service Unavailable` | `"SERVICE_UNAVAILABLE"` |
| `INTERNAL_ERROR` | Fallback | `500 Internal Server Error` | `"INTERNAL_ERROR"` |

---

## Minimum Safe Public Error Payload

All error responses produced by the Exception Middleware emit a standardized `application/json` payload structure:

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Target entity account_123 does not exist.",
  "details": null
}
```

---

## Key Architecture Principles

1. **Internal Message & Traceback Isolation**: Internal diagnostic messages (`internal_message`, database connection strings, stack traces) are logged via Phase 017 structured JSON logging and NEVER sent to HTTP clients.
2. **Unhandled Exception Protection**: Unhandled generic exceptions (`RuntimeError`, etc.) return a generic 500 `INTERNAL_ERROR` response (`"message": "An internal error occurred."`). The full stack trace is logged internally with `event="application.error"`.
3. **Secret Redaction**: Exception `details` payloads are sanitized via `sanitize_structured_data()`. Sensitive parameter keys (`password`, `api_key`, `token`, `authorization`, `bearer`) are masked as `"[REDACTED]"`.
4. **FastAPI & Route Compatibility**: Preserves standard `fastapi.HTTPException`, 404 Not Found, and 405 Method Not Allowed routes without modifying route handler definitions.
5. **Layer HTTP Isolation**: Domain, application, and infrastructure layers raise `AgentPayError` exceptions with zero dependencies on FastAPI, Starlette, or HTTP transport code.

---

## Future Phase Integration

- **Phase 019 (Current)**: Exception Middleware HTTP translation layer, status code mapping, safe public JSON payloads, structured logging, secret redaction, and `HTTPException` compatibility.
- **Phase 023**: Standardized Request Validation Error Handler.
- **Phase 025**: Response Standardization (wrapping successful and error payloads in standardized envelopes).
