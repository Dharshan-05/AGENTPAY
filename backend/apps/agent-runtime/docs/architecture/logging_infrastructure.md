# AGENTPAY Logging Infrastructure Architecture

## Overview & Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses Python's standard `logging` library to establish a centralized, environment-aware, container-native logging foundation.

```text
                    AGENTPAY
                       │
                       ▼
               Logging Infrastructure
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Console      Uvicorn      Future
       Handler       Logs       Collectors
          │
          ▼
      stdout/stderr
          │
    ┌─────┼─────────────┐
    ▼     ▼             ▼
 Docker Kubernetes     Cloud
```

---

## Key Architecture Principles

1. **Standard Python Logging**: Built on standard `logging` module (`logging.getLogger(__name__)`). No third-party logging frameworks (Loguru, Structlog) required for foundation. Structured logging transition is reserved for Phase 017.
2. **Centralized & Idempotent (`configure_logging`)**: Logging configuration is initialized via `configure_logging(settings)`. Calling `configure_logging()` multiple times is safe and prevents handler duplication.
3. **Container & Cloud-Native (`sys.stdout`)**: Primary log output targets `sys.stdout`. Persistent local file logs are avoided to allow ephemeral containers (Docker/Kubernetes) and cloud aggregators (CloudWatch, Stackdriver, Datadog) to collect logs natively.
4. **UTC ISO-8601 Timestamps (`UTCFormatter`)**: Log record timestamps are rendered in UTC with trailing `Z` (`YYYY-MM-DDTHH:MM:SSZ`).
5. **Defensive Secret Redaction (`SecretSanitizingFilter`)**: `logging.Filter` automatically sanitizes sensitive keywords (`password`, `secret`, `bearer`, `authorization`, `token`) in log messages.
6. **Framework & Domain Isolation**: Domain layer source code (`app/domain/`) is kept free from infrastructure logging dependencies.
7. **Pytest `caplog` Compatibility**: Fully compliant with Pytest log capture for testing log output.

---

## Log Output Baseline Format

```text
2026-08-25T14:50:00Z | INFO    | agentpay.lifespan | Initializing AGENTPAY application lifecycle...
```

---

## Future Phase Transitions

- **Phase 016 (Current)**: Centralized Logging Foundation (UTC ISO, stdout handler, Uvicorn sync, secret sanitization, caplog compliance).
- **Phase 017**: Structured JSON Logging (JSON log format, machine-readable event schemas, context fields).
- **Phase 018 / 019**: Global Error Handling & Exception Middleware integration.
- **Phase 024**: Request ID Middleware & Correlation ID tracing.
