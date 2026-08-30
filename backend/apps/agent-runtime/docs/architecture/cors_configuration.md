# AGENTPAY CORS Security Architecture

## Overview & Security Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses Starlette `CORSMiddleware` configured centrally in `app/middleware/registration.py`.

Cross-Origin Resource Sharing (CORS) is a **Browser Security Boundary** that controls whether frontend client applications executing in web browsers are permitted to read cross-origin HTTP responses.

> [!IMPORTANT]
> CORS is NOT an authentication or authorization mechanism. It does NOT protect APIs from direct server-to-server HTTP calls, curl scripts, or malicious non-browser clients. Authentication, authorization, and rate limiting remain separate security controls.

---

## Configuration & Environment Policy (`app/core/config.py`)

CORS policies are driven by application configuration settings (`Settings`):
- `CORS_ALLOWED_ORIGINS`: Comma-separated list or Python list of trusted frontend origin URLs (e.g. `http://localhost:3000,https://app.example.com`).
- `CORS_ALLOW_CREDENTIALS`: Boolean flag indicating whether cross-origin requests may include cookies or credentials (default `False`).

```text
               Environment Settings
              (app/core/config.py)
                        │
                        ▼
               CORSMiddleware Pipeline
          (app/middleware/registration.py)
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 Allowed Origin                  Disallowed Origin
  (Reflected + Vary)             (Headers Omitted)
```

---

## Production Security Rules & Fail-Fast Validation

To prevent enterprise vulnerability risks:
1. **No Production Wildcards**: Wildcard origin `"*"` is strictly prohibited when `APP_ENV=production`. Attempting to initialize production settings with `"*"` raises a startup `ValueError`.
2. **No Wildcard + Credentials**: Combining `cors_allowed_origins=["*"]` with `cors_allow_credentials=True` is prohibited across all environments and raises a `ValueError`.
3. **Strict Origin Format**: Origins must begin with explicit schemes (`http://` or `https://`). Malformed strings without schemes are rejected during Settings initialization.
4. **Explicit Method & Header Allowlists**:
   - Allowed Methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`
   - Allowed Headers: `Accept`, `Content-Type`, `Authorization`
   - Exposed Headers: `[]` (empty by default)

---

## Middleware Pipeline Execution Order

```text
HTTP Request → APIMiddleware → CORSMiddleware → ExceptionMiddleware → Router → Endpoint
```

1. **Preflight `OPTIONS` Handling**: Preflight requests are intercepted by `CORSMiddleware` before reaching business endpoints, returning `200 OK` with CORS headers for approved origins.
2. **Error Response Preservation**: Handled (`AgentPayError`) and unhandled (`500`) exceptions formatted by `ExceptionMiddleware` retain `Access-Control-Allow-Origin` headers, allowing cross-origin browser clients to inspect error JSON responses safely.

---

## Future Phase Integration

- **Phase 022 (Current)**: Enterprise CORS Security Configuration, origin validation, preflight handling, production safety checks, and error response compatibility.
- **Phase 023**: Request Validation.
- **Phase 024**: Request ID Middleware.
- **Phase 025**: Response Standardization.
