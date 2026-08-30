# AGENTPAY Request Validation Architecture

## Overview & Boundary Definition

The AGENTPAY backend service (`apps/agent-runtime`) uses Pydantic v2 for transport request validation at the HTTP boundary.

Request validation operates exclusively as an **Input Transport Boundary**. It verifies request payload syntax, structure, data types, value boundaries, strict field rules, and query/path parameters before inputs reach application use cases or domain entities.

> [!IMPORTANT]
> Request validation handles transport-level validation only (e.g. required fields, type bounds, UUID syntax, list limits). Business rules (e.g. user permissions, account balances, transaction legality) belong strictly in the Application and Domain layers.

---

## Strict Schema Policy (`app/schemas/requests.py`)

All API request models inherit from `StrictRequestModel`:

```python
from pydantic import BaseModel, ConfigDict


class StrictRequestModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=False,
        validate_assignment=True,
    )
```

### Key Principles
1. **Extra Field Rejection (`extra="forbid"`)**: Unexpected parameters submitted in JSON payloads or nested objects are rejected with `HTTP 400 Bad Request` instead of being silently ignored.
2. **Type Safety & Constraints**: Pydantic types (`UUID`, `Decimal`, `StrEnum`, `StrictBool`, `datetime`) enforce strict boundaries on incoming data.
3. **No I/O or Business Logic**: Validators are pure functions; they do not query databases, perform network I/O, or execute business rules.

---

## Validation Exception Normalization (`app/exceptions/handler.py` & `app/middleware/exception.py`)

FastAPI `RequestValidationError` and malformed `json.JSONDecodeError` exceptions are intercepted by `validation_exception_handler` and normalized into safe, deterministic `HTTP 400 Bad Request` responses:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": [
    {
      "location": "body.age",
      "message": "Input should be a valid integer",
      "type": "int_type"
    }
  ]
}
```

### Malformed JSON Handling
Syntax errors in JSON payloads (e.g. `{invalid_json`) produce:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid JSON payload syntax.",
  "details": null
}
```

---

## Zero Secret Leakage Policy

1. **Automatic Secret Redaction**: Validation error messages and location details inspecting sensitive fields (`password`, `token`, `secret`, `api_key`, `authorization`, `cookie`) mask values with generic messages (`"Invalid sensitive parameter value."`).
2. **Zero Response & Log Exposure**: Secret values submitted in body fields, query parameters, authorization headers, or cookies are never echoed back in HTTP response bodies or written to structured log files.

---

## Layer Isolation Architecture

```text
HTTP Request → APIMiddleware → CORSMiddleware → Request Validation → ExceptionMiddleware → Router → Application → Domain
```

- Domain and Application layers retain **zero dependencies** on FastAPI, Starlette, `RequestValidationError`, or Pydantic transport request models.
- Transport schemas remain isolated in `app/schemas/requests.py`.
