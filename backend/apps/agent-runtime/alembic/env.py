"""Alembic environment configuration module for AGENTPAY (Phase 017).

Integrates SQLAlchemy 2.0 AsyncEngine with Alembic async migration runner,
consuming dynamic database configuration from app.core.config with zero secret leakage
and environment safety guards.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.infrastructure.database.models  # noqa: F401
from alembic import context
from app.core.config import Environment, get_settings
from app.infrastructure.database.base import Base

# Alembic Config object providing access to alembic.ini settings (populated when executed via Alembic CLI)  # noqa: E501
config = getattr(context, "config", None)

# Interpret logging configuration file if present
if config is not None and config.config_file_name:
    fileConfig(config.config_file_name)


# Retrieve canonical settings
settings = get_settings()

# Target metadata for autogenerate support
target_metadata = Base.metadata


def get_database_url() -> str:
    """Retrieve canonical database connection URL from Settings, enforcing environment safety guards."""  # noqa: E501
    url = settings.effective_database_url.get_secret_value()

    # Environment safety guard: Prevent automated tests/migrations against production/staging
    if settings.app_env == Environment.TEST:
        target_lower = url.lower()
        unsafe_keywords = [
            "prod",
            "production",
            "staging",
            "rds.amazonaws.com",
            "database.azure.com",
        ]
        for keyword in unsafe_keywords:
            if keyword in target_lower:
                msg = f"Migration runner safety guard: TEST environment cannot target PROD/STAGING database ('{keyword}')."  # noqa: E501
                raise ValueError(msg)

    return url


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within a transactional synchronous runner context."""
    from sqlalchemy import text

    connection.execute(
        text(
            "CREATE TABLE IF NOT EXISTS alembic_version ("
            "version_num VARCHAR(255) NOT NULL, "
            "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
            ");"
        )
    )
    connection.execute(
        text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255);")
    )

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode producing raw SQL DDL output."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Initialize AsyncEngine and run online database migrations within an async context."""
    url = get_database_url()
    configuration = config.get_section(config.config_ini_section, {}) if config is not None else {}
    configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await connection.commit()

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode connecting directly to PostgreSQL."""
    asyncio.run(run_async_migrations())


def main() -> None:
    """Main entry point for Alembic migration execution."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


# Execute migration runner when invoked within active Alembic context
if config is not None and config.config_file_name:
    main()


