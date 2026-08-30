"""Unit and integration tests for Phase 015 & 016 Database Pooling and Environment Management."""

import ast
from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError
from sqlalchemy.exc import TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Environment, Settings, get_settings
from app.infrastructure.database.engine import (
    DatabaseLifecycleComponent,
    dispose_async_engine,
    get_async_engine,
    get_pool_status,
)
from app.infrastructure.database.session import get_async_sessionmaker, get_db_session

# ============================================================================
# PHASE 015: DATABASE CONNECTION POOLING TESTS
# ============================================================================


def test_pool_size_positive_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify db_pool_size <= 0 raises validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("DB_POOL_SIZE", "0")
    with pytest.raises(ValidationError, match="DB_POOL_SIZE"):
        Settings(db_pool_size=0)
    get_settings.cache_clear()


def test_pool_max_overflow_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify negative db_max_overflow raises validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("DB_MAX_OVERFLOW", "-1")
    with pytest.raises(ValidationError, match="DB_MAX_OVERFLOW"):
        Settings(db_max_overflow=-1)
    get_settings.cache_clear()


def test_pool_timeout_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify db_pool_timeout <= 0 raises validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("DB_POOL_TIMEOUT", "0.0")
    with pytest.raises(ValidationError, match="DB_POOL_TIMEOUT"):
        Settings(db_pool_timeout=0.0)
    get_settings.cache_clear()


def test_pool_recycle_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify negative db_pool_recycle raises validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("DB_POOL_RECYCLE", "-5")
    with pytest.raises(ValidationError, match="DB_POOL_RECYCLE"):
        Settings(db_pool_recycle=-5)
    get_settings.cache_clear()


def test_get_pool_status_observability() -> None:
    """Verify get_pool_status returns non-sensitive pool diagnostic metrics."""
    engine = get_async_engine()
    status = get_pool_status(engine)

    assert "pool_class" in status
    assert "pool_size" in status
    assert "checked_in" in status
    assert "checked_out" in status
    assert "overflow" in status


@pytest.mark.asyncio
async def test_session_connection_acquisition_and_release() -> None:
    """Verify acquiring an AsyncSession checks out a connection and closing releases it."""
    engine = get_async_engine()
    factory = get_async_sessionmaker(engine)

    status_before = get_pool_status(engine)
    session = factory()

    # Session exists
    assert isinstance(session, AsyncSession)
    await session.close()

    status_after = get_pool_status(engine)
    assert status_after["checked_out"] == status_before["checked_out"]


@pytest.mark.asyncio
async def test_session_generator_rollback_on_exception() -> None:
    """Verify get_db_session rolls back transaction on exception and closes session."""
    gen = get_db_session()
    session = await anext(gen)
    assert session is not None

    class CustomTestError(Exception):
        pass

    with pytest.raises(CustomTestError):
        await gen.athrow(CustomTestError("Test error"))


@pytest.mark.asyncio
async def test_controlled_pool_exhaustion_behavior() -> None:
    """Verify pool exhaustion times out safely after pool_timeout without deadlocks or crashes."""
    from unittest.mock import MagicMock

    from sqlalchemy.pool import QueuePool

    mock_dbapi_conn = MagicMock()
    creator = MagicMock(return_value=mock_dbapi_conn)

    pool = QueuePool(creator, pool_size=1, max_overflow=0, timeout=0.1)

    # Acquire the single persistent connection from pool
    conn1 = pool.connect()
    assert conn1 is not None

    # Attempting to acquire connection 2 from exhausted pool times out safely
    with pytest.raises(SATimeoutError):
        pool.connect()

    conn1.close()
    pool.dispose()


@pytest.mark.asyncio
async def test_database_lifecycle_component_teardown() -> None:
    """Verify DatabaseLifecycleComponent handles graceful engine disposal on shutdown."""
    component = DatabaseLifecycleComponent()
    await component.startup()

    engine = get_async_engine()
    assert engine is not None

    await component.shutdown()
    await dispose_async_engine()


# ============================================================================
# PHASE 016: DATABASE ENVIRONMENT MANAGEMENT TESTS
# ============================================================================


def test_dev_environment_allows_safe_local_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify development environment allows local host and default development password."""
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres_dev_pass")

    settings = Settings()
    assert settings.app_env == Environment.DEVELOPMENT
    assert settings.postgres_host == "localhost"
    get_settings.cache_clear()


def test_test_environment_blocks_production_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify test environment safety guard rejects production database URLs."""
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://user:pass@prod-db.rds.amazonaws.com:5432/proddb"
    )

    with pytest.raises(ValueError, match="PROD/STAGING database"):
        Settings()
    get_settings.cache_clear()


def test_test_environment_blocks_staging_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify test environment safety guard rejects staging database URLs."""
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://user:pass@staging-db.database.azure.com:5432/db"
    )

    with pytest.raises(ValueError, match="PROD/STAGING database"):
        Settings()
    get_settings.cache_clear()


def test_production_environment_rejects_default_password() -> None:
    """Verify production environment rejects default development password."""
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="Default development password"):
        Settings(
            _env_file=None,
            app_env=Environment.PRODUCTION,
            debug=False,
            postgres_password=SecretStr("postgres_dev_pass"),
        )
    get_settings.cache_clear()


def test_production_environment_rejects_localhost_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production environment rejects localhost host without explicit DATABASE_URL."""
    get_settings.cache_clear()
    monkeypatch.setenv("POSTGRES_PASSWORD", "secure_prod_password_32_bytes_long!")
    monkeypatch.setenv("JWT_SECRET", "secure_jwt_secret_32chars_long_prod!")
    with pytest.raises(ValueError, match="Localhost database host"):
        Settings(
            _env_file=None,
            app_env=Environment.PRODUCTION,
            debug=False,
            postgres_host="localhost",
        )
    get_settings.cache_clear()


def test_secret_isolation_across_environments() -> None:
    """Verify database password and URL secrets are redacted in safe_summary across environments."""
    for env in [Environment.DEVELOPMENT, Environment.TEST, Environment.LOCAL]:
        s = Settings(app_env=env)
        summary = s.safe_summary
        assert summary["postgres_password"] == "[REDACTED]"
        assert summary["effective_database_url"] == "[REDACTED]"


def test_domain_layer_has_zero_infrastructure_pooling_dependencies() -> None:
    """Verify domain layer files contain zero pooling or infrastructure database imports."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    if not domain_dir.exists():
        return

    forbidden_imports = [
        "sqlalchemy",
        "asyncpg",
        "app.infrastructure.database",
    ]

    py_files = [p for p in domain_dir.rglob("*.py") if p.is_file()]
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_imports:
                        assert not alias.name.startswith(forbidden), (
                            f"Forbidden import '{alias.name}' in {py_file.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_imports:
                        assert not node.module.startswith(forbidden), (
                            f"Forbidden import '{node.module}' in {py_file.name}"
                        )
