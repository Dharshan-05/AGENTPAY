"""Unit tests for secret configuration, SecretStr redaction, and leakage prevention."""

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from app.core.config import Settings, get_settings

FAKE_SECRET = "SUPER_FAKE_SECRET_12345678901234567890321"


def test_secret_str_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify sensitive fields are wrapped in SecretStr and redacted in repr/str output."""
    monkeypatch.setenv("SECRET_KEY", FAKE_SECRET)
    get_settings.cache_clear()

    cfg = get_settings()
    assert isinstance(cfg.secret_key, SecretStr)
    assert cfg.secret_key.get_secret_value() == FAKE_SECRET

    repr_output = repr(cfg)
    str_output = str(cfg)

    assert FAKE_SECRET not in repr_output
    assert FAKE_SECRET not in str_output
    assert "**********" in repr_output or "[REDACTED]" in repr_output
    get_settings.cache_clear()


def test_safe_summary_masking(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify safe_summary API masks sensitive fields as [REDACTED]."""
    monkeypatch.setenv("SECRET_KEY", FAKE_SECRET)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    get_settings.cache_clear()

    cfg = get_settings()
    summary = cfg.safe_summary

    assert summary["secret_key"] == "[REDACTED]"
    assert summary["database_url"] == "[REDACTED]"
    assert FAKE_SECRET not in str(summary)
    assert "user:pass" not in str(summary)
    get_settings.cache_clear()


def test_secret_key_minimum_length(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify secret keys below 32 characters raise validation error."""
    monkeypatch.setenv("SECRET_KEY", "short_secret_key_under_32_chars")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "SECRET_KEY must be at least 32 characters long" in str(exc_info.value)
    get_settings.cache_clear()


def test_empty_secret_key_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify empty string SECRET_KEY raises validation error."""
    monkeypatch.setenv("SECRET_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "SECRET_KEY cannot be empty" in str(exc_info.value)
    get_settings.cache_clear()


def test_database_url_secret_protection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify database URL is wrapped in SecretStr and redacted."""
    db_url = "postgresql://dbuser:supersecretpass@localhost:5432/agentpay"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    cfg = get_settings()
    assert isinstance(cfg.database_url, SecretStr)
    assert cfg.database_url.get_secret_value() == db_url
    assert db_url not in repr(cfg)
    assert "supersecretpass" not in repr(cfg)
    get_settings.cache_clear()


def test_redis_url_secret_protection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify redis URL is wrapped in SecretStr and redacted."""
    redis_url = "redis://:redissecretpass@localhost:6379/0"
    monkeypatch.setenv("REDIS_URL", redis_url)
    get_settings.cache_clear()

    cfg = get_settings()
    assert isinstance(cfg.redis_url, SecretStr)
    assert cfg.redis_url.get_secret_value() == redis_url
    assert redis_url not in repr(cfg)
    assert "redissecretpass" not in repr(cfg)
    get_settings.cache_clear()


def test_openapi_zero_secret_leakage(client: TestClient) -> None:
    """Verify generated OpenAPI schema contains zero secret names or values."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema_str = response.text

    forbidden_terms = ["SECRET_KEY", "DATABASE_URL", "REDIS_URL", "JWT_SECRET", "supersecretpass"]
    for term in forbidden_terms:
        assert term not in schema_str, f"Secret term '{term}' leaked into OpenAPI schema!"


def test_root_endpoint_zero_secret_leakage(client: TestClient) -> None:
    """Verify HTTP root status response contains zero secret keys or values."""
    response = client.get("/")
    assert response.status_code == 200
    body_str = response.text

    forbidden_terms = ["secret", "password", "token", "database_url", "redis_url"]
    for term in forbidden_terms:
        assert term not in body_str, f"Secret token '{term}' leaked into HTTP response payload!"
