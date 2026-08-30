"""Comprehensive unit and integration tests for Phase 013 & Phase 014 Database Foundation."""

import ast
import asyncio
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.application.services.readiness import DatabaseReadinessCheck
from app.core.config import Environment, Settings, get_settings
from app.infrastructure.database import (
    DatabaseLifecycleComponent,
    check_database_health,
    dispose_async_engine,
    get_async_engine,
    get_async_sessionmaker,
    get_db_session,
)

# ============================================================================
# PHASE 013: DATABASE CONFIGURATION MANAGEMENT TESTS
# ============================================================================


def test_database_url_normalization_postgresql_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify postgresql:// URL scheme is normalized to postgresql+asyncpg://."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://dbuser:dbpass@localhost:5432/testdb")
    get_settings.cache_clear()

    settings = get_settings()
    effective_url = settings.effective_database_url.get_secret_value()

    assert effective_url.startswith("postgresql+asyncpg://")
    assert "dbuser:dbpass@localhost:5432/testdb" in effective_url
    get_settings.cache_clear()


def test_database_url_normalization_postgres_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify postgres:// URL scheme is normalized to postgresql+asyncpg://."""
    monkeypatch.setenv("DATABASE_URL", "postgres://dbuser:dbpass@localhost:5432/testdb")
    get_settings.cache_clear()

    settings = get_settings()
    effective_url = settings.effective_database_url.get_secret_value()

    assert effective_url.startswith("postgresql+asyncpg://")
    get_settings.cache_clear()


def test_implicit_database_url_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify effective_database_url is constructed from individual fields."""

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_USER", "custom_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "custom_pass")
    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "custom_db")
    get_settings.cache_clear()

    settings = get_settings()
    effective_url = settings.effective_database_url.get_secret_value()

    assert (
        effective_url == "postgresql+asyncpg://custom_user:custom_pass@db.internal:5433/custom_db"
    )
    get_settings.cache_clear()


def test_invalid_postgres_port_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify invalid database port numbers raise validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("POSTGRES_PORT", "0")
    with pytest.raises(ValidationError):
        Settings(postgres_port=0)
    get_settings.cache_clear()


def test_invalid_pool_size_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify invalid pool sizes raise validation error."""
    get_settings.cache_clear()
    monkeypatch.setenv("DB_POOL_SIZE", "-5")
    with pytest.raises(ValidationError):
        Settings(db_pool_size=-5)
    get_settings.cache_clear()


def test_secret_redaction_for_postgres_password_and_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify postgres password and database URL are redacted in safe_summary and repr."""
    secret_pass = "super_secret_db_password_123"
    monkeypatch.setenv("POSTGRES_PASSWORD", secret_pass)
    monkeypatch.setenv(
        "DATABASE_URL", f"postgresql://postgres:{secret_pass}@localhost:5432/agentpay_dev"
    )
    get_settings.cache_clear()

    settings = get_settings()
    repr_output = repr(settings)
    summary = settings.safe_summary

    assert secret_pass not in repr_output
    assert summary["postgres_password"] == "[REDACTED]"
    assert summary["database_url"] == "[REDACTED]"
    assert summary["effective_database_url"] == "[REDACTED]"
    get_settings.cache_clear()


def test_test_environment_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify test environment configuration operates in isolated mode."""
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.is_test is True
    assert settings.environment == Environment.TEST
    get_settings.cache_clear()


# ============================================================================
# PHASE 014: ASYNCHRONOUS DATABASE CONNECTION & ENGINE TESTS
# ============================================================================


def test_async_engine_initialization() -> None:
    """Verify get_async_engine returns a valid SQLAlchemy AsyncEngine singleton."""
    engine = get_async_engine()
    assert isinstance(engine, AsyncEngine)
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "asyncpg"


@pytest.mark.asyncio
async def test_database_engine_disposal() -> None:
    """Verify dispose_async_engine disposes of the global AsyncEngine cleanly."""
    engine1 = get_async_engine()
    assert engine1 is not None

    await dispose_async_engine()
    engine2 = get_async_engine()

    assert engine2 is not engine1


def test_async_sessionmaker_factory() -> None:
    """Verify get_async_sessionmaker produces valid AsyncSession factory instances."""
    engine = get_async_engine()
    factory = get_async_sessionmaker(engine=engine)
    session = factory()

    assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_get_db_session_dependency_generator() -> None:
    """Verify get_db_session dependency yields AsyncSession and cleans up properly."""
    gen = get_db_session()
    session = await anext(gen)
    assert isinstance(session, AsyncSession)

    # Clean up generator exit
    await gen.aclose()


@pytest.mark.asyncio
async def test_check_database_health_fallback_on_unreachable_db() -> None:
    """Verify check_database_health returns False cleanly when database is unreachable."""
    invalid_settings = Settings(
        postgres_host="invalid.unreachable.host.domain",
        db_connect_timeout=0.2,
    )
    unreachable_engine = get_async_engine(settings=invalid_settings)

    is_healthy = await check_database_health(engine=unreachable_engine)
    assert is_healthy is False
    await unreachable_engine.dispose()


@pytest.mark.asyncio
async def test_database_readiness_check() -> None:
    """Verify DatabaseReadinessCheck handles database state gracefully."""
    check = DatabaseReadinessCheck()
    result = await check.check()

    assert result.name == "database"
    assert isinstance(result.ready, bool)
    assert result.details is not None


@pytest.mark.asyncio
async def test_database_lifecycle_component_startup_and_shutdown() -> None:
    """Verify DatabaseLifecycleComponent initializes engine on startup and disposes on shutdown."""
    component = DatabaseLifecycleComponent()
    assert component.name == "database_engine"

    await component.startup()
    engine = get_async_engine()
    assert isinstance(engine, AsyncEngine)

    await component.shutdown()


@pytest.mark.asyncio
async def test_concurrent_async_session_creation() -> None:
    """Verify multiple concurrent async tasks can acquire independent AsyncSession instances."""
    factory = get_async_sessionmaker()

    async def acquire_session() -> AsyncSession:
        return factory()

    sessions = await asyncio.gather(*[acquire_session() for _ in range(5)])
    assert len(sessions) == 5
    # Assert all session objects are distinct instances
    assert len(set(sessions)) == 5


def test_domain_layer_strict_database_isolation() -> None:
    """Verify domain layer files contain zero DB client or ORM imports."""
    domain_dir = Path(__file__).parent.parent.parent / "app" / "domain"
    if not domain_dir.exists():
        return

    forbidden_imports = [
        "asyncpg",
        "psycopg2",
        "psycopg",
        "sqlalchemy",
        "alembic",
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
                            f"Forbidden DB import '{alias.name}' in {py_file.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_imports:
                        assert not node.module.startswith(forbidden), (
                            f"Forbidden DB import '{node.module}' in {py_file.name}"
                        )
