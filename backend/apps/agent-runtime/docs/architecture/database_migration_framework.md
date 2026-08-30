# AGENTPAY Database Migration Framework Architecture (Phase 017)

## Executive Summary

This document specifies the database migration framework architecture for **AGENTPAY** (`Phase 017`).

The framework establishes an automated, environment-aware database schema migration pipeline using **Alembic** integrated with SQLAlchemy 2.0 and `asyncpg`, consuming authoritative database settings dynamically from `app.core.config.Settings` with zero secret exposure.

---

## 1. Migration Directory Architecture

```text
apps/agent-runtime/
├── alembic.ini                # Centralized Alembic configuration & path resolution
└── alembic/
    ├── env.py                 # Async migration runner & environment safety guards
    ├── script.py.mako         # Standardized revision file template
    └── versions/              # Target directory for versioned migration scripts
```

---

## 2. Dynamic Database Configuration Integration

Alembic's migration runner (`alembic/env.py`) imports the application's `Settings` class (`app.core.config.get_settings()`):

1. **URL Resolution**: Retrieves `settings.effective_database_url.get_secret_value()`, normalizing driver schemes to `postgresql+asyncpg://`.
2. **Zero Hardcoded Credentials**: No database hostnames, usernames, passwords, or connection strings are hardcoded in `alembic.ini` or migration scripts.
3. **Environment Safety Guard**:
   - In `APP_ENV=test` (`Environment.TEST`), any database URL pointing to production or staging databases (`prod`, `production`, `staging`, `amazonaws.com`, `azure.com`) is blocked immediately:
     ```python
     raise ValueError(
         "Migration runner safety guard: TEST environment cannot target PROD/STAGING database."
     )
     ```

---

## 3. Migration Runner Modes

- **Online Mode (`run_migrations_online`)**: Initializes an `AsyncEngine` using `async_engine_from_config`, acquires an async connection, and executes migrations inside a synchronous transaction wrapper (`connection.run_sync(do_run_migrations)`).
- **Offline Mode (`run_migrations_offline`)**: Renders static SQL DDL scripts (`literal_binds=True`) for dry-run inspection without database connectivity.

---

## 4. CLI Workflow Commands

| Operation | Command Line Syntax | Description |
| :--- | :--- | :--- |
| **Inspect Current Version** | `alembic current` | Display current applied migration revision |
| **Inspect Heads** | `alembic heads` | Display current migration heads |
| **Inspect History** | `alembic history` | Display chronological migration revision graph |
| **Create Revision** | `alembic revision -m "description"` | Generate new revision script in `alembic/versions/` |
| **Apply Migrations** | `alembic upgrade head` | Apply all pending migrations to target database |
| **Revert Last Migration** | `alembic downgrade -1` | Revert the most recent migration revision |
