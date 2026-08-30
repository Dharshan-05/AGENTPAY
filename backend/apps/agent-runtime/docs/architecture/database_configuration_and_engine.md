# AGENTPAY Database Configuration & Async Engine Architecture (Phase 013 + Phase 014)

## Executive Summary

This document formalizes the centralized database configuration management (`Phase 013`) and asynchronous PostgreSQL engine layer (`Phase 014`) for the **AGENTPAY** platform (`apps/agent-runtime`).

The implementation establishes a strongly-typed, validated settings model and a high-performance SQLAlchemy 2.0 + asyncpg connection engine, providing request-scoped session management, zero secret leakage, fail-closed readiness checks, and clean lifespan disposal.

---

## 1. Database Configuration Architecture (Phase 013)

### Configuration Settings Model (`app/core/config.py`)

Database connection and pooling parameters are integrated into the canonical `Settings` class using Pydantic v2:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `POSTGRES_USER` | `str` | `"postgres"` | PostgreSQL database user name |
| `POSTGRES_PASSWORD` | `SecretStr` | `"postgres_dev_pass"` | Protected database user password |
| `POSTGRES_HOST` | `str` | `"localhost"` | Hostname or container IP address |
| `POSTGRES_PORT` | `int` | `5432` | TCP port number (validated `1..65535`) |
| `POSTGRES_DB` | `str` | `"agentpay_dev"` | Database name |
| `DATABASE_URL` | `SecretStr \| None` | `None` | Explicit database connection URL string |
| `DB_POOL_SIZE` | `int` | `10` | Base connection pool size |
| `DB_MAX_OVERFLOW` | `int` | `20` | Maximum pool burst overflow connection count |
| `DB_POOL_TIMEOUT` | `float` | `30.0` | Connection acquisition wait timeout (seconds) |
| `DB_POOL_RECYCLE` | `int` | `1800` | Connection recycle lifetime (seconds) |
| `DB_POOL_PRE_PING` | `bool` | `True` | Connection liveness probe before execution |
| `DB_CONNECT_TIMEOUT` | `float` | `10.0` | Driver TCP connection establishment timeout |
| `DB_COMMAND_TIMEOUT` | `float` | `30.0` | Per-statement execution timeout (seconds) |

### Scheme Normalization & URL Assembly (`effective_database_url`)

The application normalizes incoming database URLs to ensure compatibility with SQLAlchemy 2.0's async driver scheme:
- `postgresql://...` -> `postgresql+asyncpg://...`
- `postgres://...` -> `postgresql+asyncpg://...`
- Absence of `DATABASE_URL` -> Dynamically constructs `postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}`.

---

## 2. Asynchronous Engine & Session Architecture (Phase 014)

```text
                  FastAPI Controller / Endpoint Request
                                     │
                                     ▼
                     get_db_session() [FastAPI Dependency]
                                     │
                                     ▼
                     AsyncSession Factory (async_sessionmaker)
                                     │
                                     ▼
                 SQLAlchemy 2.0 AsyncEngine (get_async_engine)
                                     │
                                     ▼
                      asyncpg Driver (Connection Pool)
                                     │
                                     ▼
                      PostgreSQL 15+ Database Service
```

### Engine Layer (`app/infrastructure/database/engine.py`)

- **Singleton Pattern**: `get_async_engine()` lazily initializes a thread-safe `AsyncEngine` singleton using normalized configuration.
- **Teardown Lifecycle**: `dispose_async_engine()` executes `await engine.dispose()` during application shutdown via `DatabaseLifecycleComponent`.

### Session Layer (`app/infrastructure/database/session.py`)

- **Session Dependency (`get_db_session`)**: Request-scoped async generator for FastAPI endpoints:
  ```python
  async with session_factory() as session:
      try:
          yield session
          await session.commit()
      except Exception:
          await session.rollback()
          raise
  ```
- **Health Check (`check_database_health`)**: Executes `SELECT 1` via `AsyncSession` to verify database connectivity without leaking connection string secrets or exposing internal tracebacks.

---

## 3. Security & Secret Protection Guarantees

1. **Zero Secret Exposure**: Database passwords and `DATABASE_URL` strings are wrapped in `SecretStr` and automatically masked as `"[REDACTED]"` in `safe_summary`, `repr()`, structured log events, and OpenAPI schemas.
2. **Domain Isolation**: The `app/domain/` boundary contains zero imports of `sqlalchemy`, `asyncpg`, or database infrastructure adapters.
