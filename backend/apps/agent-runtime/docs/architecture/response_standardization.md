# AGENTPAY Response Standardization Architecture

## Overview & Design Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses a canonical, deterministic HTTP response architecture across all API application endpoints.

Every API payload returned to clients adheres to a machine-readable, frontend-friendly contract that guarantees:
1. **Deterministic Structure**: Standardized top-level keys (`success`, `data`, `meta` for success; `success`, `error`, `meta` for errors).
2. **Request Correlation**: `meta.request_id` matches the `request.state.request_id` and the `X-Request-ID` HTTP response header.
3. **HTTP Semantics Preservation**: Native HTTP status codes (200, 201, 202, 204, 400, 401, 403, 404, 405, 409, 500, 503) are preserved as authoritative status indicators.
4. **HTTP 204 Bodyless Rule**: `204 No Content` responses remain completely bodyless while carrying the `X-Request-ID` response header.
5. **Zero Double Wrapping**: Already-wrapped envelopes, documentation routes (`/openapi.json`, `/docs`, `/redoc`), `HEAD` requests, and non-JSON media types bypass transformation.

---

## Canonical Success Contract

```json
{
  "success": true,
  "data": {
    "service": "agentpay-api",
    "status": "running"
  },
  "meta": {
    "request_id": "7f5e9d2b-2d43-4f5f-9e89-1e6c3f5a7b21"
  }
}
```

### Success Pydantic Model (`app/schemas/common.py`)

```python
class ResponseMeta(BaseModel):
    request_id: str = Field(..., description="Unique correlation request ID")
    timestamp: str | None = Field(default=None, description="ISO-8601 UTC timestamp")


class SuccessResponse(BaseModel, Generic[T]):
    success: Literal[True] = Field(default=True, description="Success status indicator")
    data: T = Field(..., description="Response payload data")
    meta: ResponseMeta = Field(..., description="Response metadata envelope")
```

---

## Canonical Error Contract

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [
      {
        "location": "body.amount",
        "message": "Input should be greater than 0",
        "type": "greater_than"
      }
    ]
  },
  "meta": {
    "request_id": "7f5e9d2b-2d43-4f5f-9e89-1e6c3f5a7b21"
  }
}
```

### Error Pydantic Model (`app/schemas/errors.py`)

```python
class ErrorPayload(BaseModel):
    code: str = Field(..., description="Machine-readable error classification code")
    message: str = Field(..., description="Human-readable summary message")
    details: Any | None = Field(
        default=None, description="Granular error details or validation list"
    )


class ErrorResponse(BaseModel):
    success: Literal[False] = Field(default=False, description="Failure status indicator")
    error: ErrorPayload = Field(..., description="Structured error payload")
    meta: ResponseMeta = Field(..., description="Response metadata envelope")
```

---

## Frontend & Integration Contract

Frontend and API clients can reliably inspect response payloads:

```typescript
if (response.success) {
  // Access payload data safely
  console.log(response.data);
} else {
  // Handle error taxonomy
  console.error(response.error.code, response.error.message, response.error.details);
}
console.log("Request Correlation ID:", response.meta.request_id);
```

---

## Excluded / Unwrapped Response Types

The `ResponseStandardizationMiddleware` (`app/middleware/response.py`) explicitly skips:
- **HTTP 204 No Content**: Remains bodyless to respect RFC 7230 semantics.
- **OpenAPI Schema (`/openapi.json`)**: Raw JSON schema for Swagger/ReDoc generators.
- **Documentation Interfaces (`/docs`, `/redoc`)**: HTML pages for interactive API documentation.
- **HEAD Requests**: Bodyless headers-only requests.
- **Non-JSON Media Types**: HTML, images, octet streams, file downloads.
- **Already-Standardized Envelopes**: Payloads containing top-level `success` key (prevents double wrapping).
