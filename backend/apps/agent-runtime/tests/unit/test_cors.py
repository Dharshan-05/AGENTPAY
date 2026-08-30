"""Unit, integration, and security tests for Phase 022 CORS Configuration."""

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Environment, Settings, get_settings
from app.domain.exceptions import EntityNotFoundError
from app.main import create_app


def test_cors_allowed_origin() -> None:
    """Verify explicit allowed origin receives Access-Control-Allow-Origin header."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "Origin" in response.headers.get("vary", "")


def test_cors_disallowed_origin() -> None:
    """Verify disallowed origin does not receive Access-Control-Allow-Origin header."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/", headers={"Origin": "https://evil.example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_options_preflight_allowed() -> None:
    """Verify preflight OPTIONS request for allowed origin returns CORS approval headers."""
    app = create_app()
    client = TestClient(app)

    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization",
    }
    response = client.options("/api/v1", headers=headers)

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "content-type" in response.headers.get("access-control-allow-headers", "").lower()


def test_cors_options_preflight_disallowed() -> None:
    """Verify preflight OPTIONS request for disallowed origin omits CORS headers."""
    app = create_app()
    client = TestClient(app)

    headers = {
        "Origin": "https://untrusted.example.com",
        "Access-Control-Request-Method": "DELETE",
    }
    response = client.options("/api/v1", headers=headers)

    assert "access-control-allow-origin" not in response.headers


def test_cors_comma_separated_origins_parsing() -> None:
    """Verify comma-separated origin string is parsed and normalized correctly."""
    settings = Settings(
        secret_key=SecretStr("a" * 32),
        cors_allowed_origins="http://localhost:3000 , https://app.example.com/ ",
    )
    assert settings.cors_allowed_origins == ["http://localhost:3000", "https://app.example.com"]


def test_cors_malformed_origin_rejection() -> None:
    """Verify malformed origin formats without http:// or https:// raise ValueError."""
    with pytest.raises(ValueError, match="Invalid CORS origin format"):
        Settings(
            secret_key=SecretStr("a" * 32),
            cors_allowed_origins="invalid-origin-without-scheme",
        )


def test_cors_production_wildcard_rejection() -> None:
    """Verify PRODUCTION environment rejects wildcard origin '*'."""
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="prohibited in PRODUCTION"):
        Settings(
            _env_file=None,
            secret_key=SecretStr("a" * 32),
            jwt_secret=SecretStr("secure_jwt_secret_32chars_long_prod!"),
            postgres_password=SecretStr("secure_prod_password_32_bytes_long!"),
            postgres_host="prod-db.internal",
            app_env=Environment.PRODUCTION,
            debug=False,
            cors_allowed_origins="*",
        )
    get_settings.cache_clear()


def test_cors_wildcard_credentials_rejection() -> None:
    """Verify wildcard origin '*' combined with allow_credentials=True raises ValueError."""
    with pytest.raises(ValueError, match="cannot be combined with allow_credentials"):
        Settings(
            secret_key=SecretStr("a" * 32),
            cors_allowed_origins="*",
            cors_allow_credentials=True,
        )


def test_cors_handled_exception_retains_cors_headers() -> None:
    """Verify AgentPayError responses retain CORS headers for allowed origins."""
    test_app = create_app()

    @test_app.get("/test-cors-error")
    def cors_err_route() -> None:
        raise EntityNotFoundError("Entity not found.")

    client = TestClient(test_app)
    response = client.get("/test-cors-error", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 404
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_unhandled_exception_retains_cors_headers() -> None:
    """Verify unhandled Exception 500 responses retain CORS headers for allowed origins."""
    test_app = create_app()

    @test_app.get("/test-cors-500")
    def cors_500_route() -> None:
        raise RuntimeError("Fatal error")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/test-cors-500", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 500
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
