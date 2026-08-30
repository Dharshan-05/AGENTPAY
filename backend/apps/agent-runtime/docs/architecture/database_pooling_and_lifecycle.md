# AGENTPAY Database Connection Pooling & Lifecycle Integration (Phase 015)

## Executive Summary

This document specifies the connection pooling, acquisition/release semantics, exhaustion resilience, observability metrics, and graceful teardown lifecycle for the **AGENTPAY** asynchronous PostgreSQL database layer (`Phase 015`).

---

## 1. Connection Pool Parameters & Semantics

The SQLAlchemy 2.0 `AsyncEngine` pool is configured via the centralized `Settings` class (`app/core/config.py`):

| Parameter | Type | Default | Hardening & Constraints |
| :--- | :--- | :--- | :--- |
| `db_pool_size` | `int` | `10` | Persistent connection pool size (`> 0`) |
| `db_max_overflow` | `int` | `20` | Maximum temporary burst connection overflow (`>= 0`) |
| `db_pool_timeout` | `float` | `30.0` | Maximum wait duration before pool timeout (`> 0.0` s) |
| `db_pool_recycle` | `int` | `1800` | Connection recycle threshold (`>= 0` s) |
| `db_pool_pre_ping` | `bool` | `True` | Automated `SELECT 1` ping before connection checkout |

**Theoretical Max Concurrency**: $\text{Max Connections} = \text{db\_pool\_size} + \text{db\_max\_overflow}$ (default: $10 + 20 = 30$ active connections per instance).

---

## 2. Connection Acquisition & Release Lifecycle

```text
               HTTP Request / Async Task
                          │
                          ▼
            get_db_session() [FastAPI Dependency]
                          │
                          ▼
         AsyncSession Factory (async_sessionmaker)
                          │
            1. Acquire Connection from QueuePool
                          │
                          ▼
             Execute SQL Queries / Workload
                          │
          ┌───────────────┴───────────────┐
          │ (Success)                     │ (Unhandled Exception)
          ▼                               ▼
    session.commit()              session.rollback()
          │                               │
          └───────────────┬───────────────┘
                          │
             2. Return Connection to Pool (session.close())
```

### Release Invariants
- Connection release occurs in `finally:` blocks via `session.close()`, guaranteeing no checked-out connection leaks on success, failure, transaction rollback, or async task cancellation.

---

## 3. Exhaustion & Timeout Resilience

When connection demand exceeds $\text{db\_pool\_size} + \text{db\_max_overflow}$:
1. Incoming checkout requests wait up to `db_pool_timeout` seconds ($30.0$ s).
2. If a connection becomes available, checkout succeeds cleanly.
3. If `db_pool_timeout` expires, SQLAlchemy raises `TimeoutError` without deadlocking the asyncio event loop or crashing the process.

---

## 4. Pool Observability API (`get_pool_status`)

The `get_pool_status()` helper (`app/infrastructure/database/engine.py`) provides safe non-sensitive diagnostic metrics:

```json
{
  "pool_class": "QueuePool",
  "pool_size": 10,
  "checked_in": 9,
  "checked_out": 1,
  "overflow": 0
}
```

---

## 5. Graceful Teardown Lifecycle

During application shutdown (`app/core/lifespan.py`):
1. Service state transitions to `STOPPING` (traffic readiness gated via HTTP 503).
2. Active requests complete or close sessions.
3. `DatabaseLifecycleComponent.shutdown()` invokes `dispose_async_engine()`.
4. `await engine.dispose()` closes all pool connections cleanly.
