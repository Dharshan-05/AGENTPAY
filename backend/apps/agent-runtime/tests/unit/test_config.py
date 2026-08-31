"""Unit tests for configuration management, typing, caching, and validation."""

import pytest
from pydantic import ValidationError

from app.core.config import Environment, LogLevel, Settings, get_settings


def test_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify default settings values and correct type assignments."""
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    get_settings.cache_clear()
    cfg = Settings(_env_file=None)

    assert cfg.app_name == "AGENTPAY API"
    assert cfg.app_version == "1.0.0"
    assert cfg.app_env == Environment.DEVELOPMENT
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 8000
    assert cfg.log_level == LogLevel.INFO
    assert cfg.database_url is None
    assert cfg.redis_url is None




def test_get_settings_caching() -> None:
    """Verify get_settings returns a cached singleton instance and cache_clear resets it."""
    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

    get_settings.cache_clear()
    s3 = get_settings()
    assert s1 is not s3


def test_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify environment variables correctly override configuration fields."""
    monkeypatch.setenv("APP_NAME", "AGENTPAY OVERRIDE TEST")
    monkeypatch.setenv("PORT", "9090")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEBUG", "true")

    get_settings.cache_clear()
    cfg = get_settings()

    assert cfg.app_name == "AGENTPAY OVERRIDE TEST"
    assert cfg.port == 9090
    assert cfg.log_level == LogLevel.DEBUG
    assert cfg.debug is True

    # Clean up cache
    get_settings.cache_clear()


def test_invalid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify invalid APP_ENV values raise validation error."""
    monkeypatch.setenv("APP_ENV", "invalid_environment")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "APP_ENV" in str(exc_info.value)
    get_settings.cache_clear()


def test_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify out-of-range port numbers raise validation error."""
    monkeypatch.setenv("PORT", "99999")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "PORT" in str(exc_info.value)
    get_settings.cache_clear()


def test_production_safety(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production safety rule: DEBUG cannot be enabled in PRODUCTION."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "true")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "DEBUG mode cannot be enabled in PRODUCTION environment" in str(exc_info.value)
    get_settings.cache_clear()


def test_backward_compatible_properties() -> None:
    """Verify backward-compatible properties operate correctly for main/router integration."""
    get_settings.cache_clear()
    cfg = get_settings()

    assert cfg.title == cfg.app_name
    assert cfg.version == cfg.app_version
    assert cfg.api_v1_str == "/api/v1"
    assert cfg.docs_url == "/docs"
    assert cfg.redoc_url == "/redoc"
    assert cfg.openapi_url == "/openapi.json"


def test_documentation_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify disabling documentation settings sets URL properties to None."""
    monkeypatch.setenv("DOCS_ENABLED", "false")
    monkeypatch.setenv("REDOC_ENABLED", "false")
    monkeypatch.setenv("OPENAPI_ENABLED", "false")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.docs_url is None
    assert cfg.redoc_url is None
    assert cfg.openapi_url is None
    get_settings.cache_clear()
