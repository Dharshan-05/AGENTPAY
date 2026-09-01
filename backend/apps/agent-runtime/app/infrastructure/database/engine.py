"""Asynchronous PostgreSQL database engine module for AGENTPAY (Phase 014)."""

import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import Settings, get_settings
from app.core.lifespan import LifecycleComponent

logger = logging.getLogger("agentpay.infrastructure.database")

_async_engine: AsyncEngine | None = None


def get_async_engine(settings: Settings | None = None) -> AsyncEngine:
    """Retrieve or initialize the canonical application AsyncEngine singleton."""
    global _async_engine
    if _async_engine is not None:
        return _async_engine

    current_settings = settings if settings is not None else get_settings()
    connection_url = current_settings.effective_database_url.get_secret_value()

    logger.info(
        "Initializing SQLAlchemy 2.0 AsyncEngine...",
        extra={
            "event": "database.engine_init",
            "postgres_host": current_settings.postgres_host,
            "postgres_port": current_settings.postgres_port,
            "postgres_db": current_settings.postgres_db,
            "pool_size": current_settings.db_pool_size,
            "max_overflow": current_settings.db_max_overflow,
        },
    )

    _async_engine = create_async_engine(
        url=connection_url,
        echo=current_settings.debug,
        pool_size=current_settings.db_pool_size,
        max_overflow=current_settings.db_max_overflow,
        pool_timeout=current_settings.db_pool_timeout,
        pool_recycle=current_settings.db_pool_recycle,
        pool_pre_ping=current_settings.db_pool_pre_ping,
        connect_args={
            "command_timeout": current_settings.db_command_timeout,
            "timeout": current_settings.db_connect_timeout,
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
    )

    return _async_engine


async def dispose_async_engine() -> None:
    """Cleanly dispose of the global AsyncEngine connection pool resources."""
    global _async_engine
    if _async_engine is not None:
        logger.info(
            "Disposing database AsyncEngine connection pool...",
            extra={"event": "database.engine_dispose"},
        )
        await _async_engine.dispose()
        _async_engine = None


def get_pool_status(engine: AsyncEngine | None = None) -> dict[str, int | str]:
    """Return non-sensitive diagnostic snapshot of database connection pool metrics."""
    target_engine = engine if engine is not None else get_async_engine()
    pool = target_engine.pool

    status: dict[str, int | str] = {
        "pool_class": pool.__class__.__name__,
    }

    if hasattr(pool, "size"):
        status["pool_size"] = pool.size()
    if hasattr(pool, "checkedin"):
        status["checked_in"] = pool.checkedin()
    if hasattr(pool, "checkedout"):
        status["checked_out"] = pool.checkedout()
    if hasattr(pool, "overflow"):
        status["overflow"] = pool.overflow()

    return status


class DatabaseLifecycleComponent(LifecycleComponent):
    """Database engine lifecycle component managing startup initialization and shutdown teardown."""

    @property
    def name(self) -> str:
        """Component identifier name."""
        return "database_engine"

    async def startup(self) -> None:
        """Initialize database AsyncEngine during application startup."""
        get_async_engine()

    async def shutdown(self) -> None:
        """Dispose database AsyncEngine during application shutdown."""
        await dispose_async_engine()
