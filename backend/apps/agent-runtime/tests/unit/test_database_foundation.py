"""Unit and integration tests for Phase 011 and Phase 012 Database Foundation."""

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import get_settings


def test_database_url_default_loading(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify DATABASE_URL loads correctly and is stored as SecretStr."""
    test_url = "postgresql://postgres:postgres_dev_pass@localhost:5432/agentpay_dev"
    monkeypatch.setenv("DATABASE_URL", test_url)
    get_settings.cache_clear()

    settings = get_settings()
    assert isinstance(settings.database_url, SecretStr)
    assert settings.database_url.get_secret_value() == test_url
    get_settings.cache_clear()


def test_database_url_redacted_in_safe_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify safe_summary redacts database credentials."""
    test_url = "postgresql://user:secretpassword@localhost:5432/agentpay_dev"
    monkeypatch.setenv("DATABASE_URL", test_url)
    get_settings.cache_clear()

    settings = get_settings()
    summary = settings.safe_summary

    assert summary["database_url"] == "[REDACTED]"
    assert "secretpassword" not in str(summary)
    get_settings.cache_clear()


def test_database_url_redacted_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify repr(settings) masks DATABASE_URL value."""
    test_url = "postgresql://user:secretpassword@localhost:5432/agentpay_dev"
    monkeypatch.setenv("DATABASE_URL", test_url)
    get_settings.cache_clear()

    settings = get_settings()
    repr_str = repr(settings)

    assert "secretpassword" not in repr_str
    get_settings.cache_clear()


def test_openapi_zero_database_secret_leakage(client: TestClient) -> None:
    """Verify generated OpenAPI schema contains zero database connection credentials."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema_text = response.text

    forbidden_terms = ["postgres_dev_pass", "secretpassword", "DATABASE_URL"]
    for term in forbidden_terms:
        assert term not in schema_text, f"Database secret term '{term}' leaked in OpenAPI schema!"


def test_domain_layer_has_zero_db_client_or_orm_dependencies() -> None:
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
        "tortoise",
        "peewee",
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


def test_docker_compose_file_exists_and_contains_postgres_service() -> None:
    """Verify docker-compose.yml exists and defines agentpay-postgres service."""
    compose_path = Path(__file__).parent.parent.parent.parent.parent / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml not found at {compose_path}"

    content = compose_path.read_text(encoding="utf-8")
    assert "agentpay-postgres" in content
    assert "postgres:15-alpine" in content or "postgres:" in content
    assert ":5432" in content
    assert "pg_isready" in content
    assert "postgres_data:" in content
