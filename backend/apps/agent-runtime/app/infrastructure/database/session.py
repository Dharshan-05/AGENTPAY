"""Asynchronous PostgreSQL session factory and dependency module (Phase 014)."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.infrastructure.database.engine import get_async_engine

logger = logging.getLogger("agentpay.infrastructure.database")

_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_async_sessionmaker(
    engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Retrieve or construct the canonical AsyncSession factory."""
    global _async_session_factory
    target_engine = engine if engine is not None else get_async_engine()

    if _async_session_factory is None or engine is not None:
        _async_session_factory = async_sessionmaker(
            bind=target_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a scoped AsyncSession per request.

    Guarantees session cleanup, rollback on unhandled exceptions, and clean closure.
    """
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(
                f"Database session rolled back due to error: {exc}",
                extra={"event": "database.session_rollback", "error": str(exc)},
            )
            raise


async def check_database_health(engine: AsyncEngine | None = None) -> bool:
    """Execute lightweight SELECT 1 connectivity probe to verify database health."""
    try:
        session_factory = get_async_sessionmaker(engine=engine)
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            return value == 1
    except Exception as exc:
        logger.warning(
            f"Database health check query failed: {exc}",
            extra={"event": "database.health_check_failed", "error": str(exc)},
        )
        return False
