"""Unit tests for environment management, properties, switching, and safety enforcement."""

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings, get_settings


def test_environment_properties_local(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify boolean properties when APP_ENV is set to local."""
    monkeypatch.setenv("APP_ENV", "local")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.environment == Environment.LOCAL
    assert cfg.is_local is True
    assert cfg.is_development is False
    assert cfg.is_test is False
    assert cfg.is_staging is False
    assert cfg.is_production is False
    get_settings.cache_clear()


def test_environment_properties_development(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify boolean properties when APP_ENV is set to development."""
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.environment == Environment.DEVELOPMENT
    assert cfg.is_local is False
    assert cfg.is_development is True
    assert cfg.is_test is False
    assert cfg.is_staging is False
    assert cfg.is_production is False
    get_settings.cache_clear()


def test_environment_properties_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify boolean properties when APP_ENV is set to test."""
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.environment == Environment.TEST
    assert cfg.is_local is False
    assert cfg.is_development is False
    assert cfg.is_test is True
    assert cfg.is_staging is False
    assert cfg.is_production is False
    get_settings.cache_clear()


def test_environment_properties_staging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify boolean properties when APP_ENV is set to staging."""
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.environment == Environment.STAGING
    assert cfg.is_local is False
    assert cfg.is_development is False
    assert cfg.is_test is False
    assert cfg.is_staging is True
    assert cfg.is_production is False
    get_settings.cache_clear()


def test_environment_properties_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify boolean properties when APP_ENV is set to production with DEBUG=false."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secure_prod_password_32_bytes!")
    monkeypatch.setenv("POSTGRES_HOST", "db.prod.internal")
    monkeypatch.setenv("JWT_SECRET", "super_secret_production_jwt_key_minimum_32_chars!")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.environment == Environment.PRODUCTION
    assert cfg.is_local is False
    assert cfg.is_development is False
    assert cfg.is_test is False
    assert cfg.is_staging is False
    assert cfg.is_production is True
    get_settings.cache_clear()


def test_environment_switching(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify settings dynamically switch environment identity across configurations."""
    for env_name in ["local", "development", "test", "staging"]:
        monkeypatch.setenv("APP_ENV", env_name)
        get_settings.cache_clear()
        assert get_settings().environment == Environment(env_name)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secure_prod_password_32_bytes!")
    monkeypatch.setenv("POSTGRES_HOST", "db.prod.internal")
    monkeypatch.setenv("JWT_SECRET", "super_secret_production_jwt_key_minimum_32_chars!")
    get_settings.cache_clear()
    assert get_settings().environment == Environment.PRODUCTION
    get_settings.cache_clear()


def test_production_debug_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production environment rejects DEBUG=true mode."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("JWT_SECRET", "super_secret_production_jwt_key_minimum_32_chars!")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "DEBUG mode cannot be enabled in PRODUCTION environment" in str(exc_info.value)
    get_settings.cache_clear()


def test_production_weak_jwt_secret_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production environment rejects default or weak JWT_SECRET."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secure_prod_password_32_bytes!")
    monkeypatch.setenv("POSTGRES_HOST", "db.prod.internal")
    monkeypatch.setenv("JWT_SECRET", "dev_jwt_secret_change_in_production_32chars_min")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "Default or weak JWT_SECRET is prohibited in PRODUCTION environment" in str(
        exc_info.value
    )
    get_settings.cache_clear()


def test_invalid_environment_fail_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify invalid APP_ENV values fail fast with validation error."""
    monkeypatch.setenv("APP_ENV", "unsupported_env")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "APP_ENV" in str(exc_info.value)
    get_settings.cache_clear()


def test_ci_cd_container_env_injection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify settings load cleanly from process environment variables."""

    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("APP_NAME", "AGENTPAY STAGING CI")
    get_settings.cache_clear()

    cfg = get_settings()
    assert cfg.app_env == Environment.STAGING
    assert cfg.port == 8080
    assert cfg.debug is False
    assert cfg.app_name == "AGENTPAY STAGING CI"
    get_settings.cache_clear()
