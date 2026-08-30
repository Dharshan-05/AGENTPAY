# AGENTPAY Structured Logging Architecture

## Overview & Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses a production-grade, single-line JSON structured logging architecture built on top of the Phase 016 Python `logging` foundation.

```text
                    AGENTPAY Application
                             │
                             ▼
                    JSONFormatter / Filter
                             │
                             ▼
                       stdout Stream
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
         Docker          Kubernetes         Cloud
       Container         Pod Logs         Aggregators
```

---

## Single-Line JSON Event Schema

Every application log event emits a valid, single-line JSON object formatted by `JSONFormatter` in `app/core/logging.py`:

```json
{
  "timestamp": "2026-08-25T15:00:00Z",
  "level": "INFO",
  "logger": "agentpay.lifespan",
  "message": "Initializing AGENTPAY application lifecycle...",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0",
  "event": "application.startup"
}
```

---

## Schema Field Specification

| Field Name | Type | Description | Mandatory |
| :--- | :--- | :--- | :--- |
| `timestamp` | `string` | ISO-8601 UTC timestamp ending in `Z` (`YYYY-MM-DDTHH:MM:SSZ`) | Yes |
| `level` | `string` | Uppercase log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | Yes |
| `logger` | `string` | Python logger namespace (`agentpay.lifespan`, `agentpay.config`) | Yes |
| `message` | `string` | Primary human-readable log event message | Yes |
| `service` | `string` | Application identity from `Settings.app_name` (`"AGENTPAY API"`) | Yes |
| `environment` | `string` | Deployment environment from `Settings.app_env` (`"development"`) | Yes |
| `version` | `string` | Service semantic version from `Settings.app_version` (`"1.0.0"`) | Yes |
| `event` | `string` | Standardized event classification (e.g. `application.startup`) | Optional |
| `exception` | `object` | Structured exception payload containing `type`, `message`, `traceback` | Optional |

---

## Recursive Nested Secret Redaction

Structured log attributes passed via `extra={...}` or dictionary payloads undergo recursive case-insensitive redaction via `sanitize_structured_data()`.

Sensitive keys matching patterns (`password`, `secret`, `token`, `api_key`, `authorization`, `bearer`, `cookie`, `private_key`) are automatically rendered as `"[REDACTED]"`.

```json
{
  "timestamp": "2026-08-25T15:00:00Z",
  "level": "INFO",
  "logger": "agentpay.config",
  "message": "Configuration parameters initialized",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0",
  "credentials": {
    "username": "admin",
    "password": "[REDACTED]"
  }
}
```

---

## Structured Exception Payload Schema

When logging exceptions (`logger.exception(...)`), exception details are encapsulated in a structured `exception` object:

```json
{
  "timestamp": "2026-08-25T15:00:00Z",
  "level": "ERROR",
  "logger": "agentpay.api",
  "message": "Failed to execute request",
  "service": "AGENTPAY API",
  "environment": "development",
  "version": "1.0.0",
  "exception": {
    "type": "ValueError",
    "message": "Invalid parameter value",
    "traceback": "Traceback (most recent call last):\n..."
  }
}
```

---

## Future Phase Integration

- **Phase 017 (Current)**: Structured JSON Logging foundation with UTC ISO timestamps, service metadata, event fields, nested secret redaction, and exception formatting.
- **Phase 018 / 019**: Global Error Handling & Exception Middleware integration.
- **Phase 024**: Request ID Middleware integration (attaching `request_id` to log event contexts).
