"""Unit and integration tests for Phase 019 Exception Middleware and HTTP translation."""

import json
import logging

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.application.exceptions import ApplicationConflictError, UseCaseError
from app.core.logging import configure_logging
from app.domain.exceptions import EntityNotFoundError
from app.exceptions.config_exceptions import ConfigurationError
from app.infrastructure.exceptions import ExternalServiceError
from app.main import create_app
from app.middleware.exception import build_error_response


def test_build_error_response_structure() -> None:
    """Verify build_error_response generates standardized JSON error responses."""
    resp = build_error_response(
        code="RESOURCE_NOT_FOUND",
        message="Resource missing.",
        details={"id": "123"},
        status_code=status.HTTP_404_NOT_FOUND,
        request_id="req-123",
    )
    assert resp.status_code == 404

    body = json.loads(resp.body)
    assert body == {
        "success": False,
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "Resource missing.",
            "details": {"id": "123"},
        },
        "meta": {
            "request_id": "req-123",
        },
    }


def test_exception_middleware_entity_not_found_404() -> None:
    """Verify EntityNotFoundError translates to 404 HTTP JSON response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-not-found")
    def not_found_route() -> None:
        raise EntityNotFoundError("Target entity account_123 does not exist.")

    client = TestClient(test_app)
    response = client.get("/test-not-found")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Target entity account_123 does not exist."
    assert data["error"]["details"] is None
    assert data["meta"]["request_id"] is not None


def test_exception_middleware_conflict_409() -> None:
    """Verify ApplicationConflictError translates to 409 HTTP JSON response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-conflict")
    def conflict_route() -> None:
        raise ApplicationConflictError("Transaction reference already processed.")

    client = TestClient(test_app)
    response = client.get("/test-conflict")

    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_CONFLICT"
    assert data["error"]["message"] == "Transaction reference already processed."


def test_exception_middleware_use_case_error_400() -> None:
    """Verify UseCaseError translates to 400 HTTP JSON response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-use-case-error")
    def use_case_route() -> None:
        raise UseCaseError("Invalid use case parameters.")

    client = TestClient(test_app)
    response = client.get("/test-use-case-error")

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "APPLICATION_ERROR"


def test_exception_middleware_configuration_error_500() -> None:
    """Verify ConfigurationError translates to 500 HTTP JSON response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-config-error")
    def config_route() -> None:
        raise ConfigurationError("Database connection string invalid.")

    client = TestClient(test_app)
    response = client.get("/test-config-error")

    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CONFIGURATION"


def test_exception_middleware_external_service_error_503() -> None:
    """Verify ExternalServiceError translates to 503 HTTP JSON response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-ext-error")
    def ext_route() -> None:
        raise ExternalServiceError("Gateway API timeout.")

    client = TestClient(test_app)
    response = client.get("/test-ext-error")

    assert response.status_code == 503
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_exception_middleware_unhandled_exception_generic_500() -> None:
    """Verify unhandled generic Exception translates to safe generic 500 response."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-unhandled")
    def unhandled_route() -> None:
        raise RuntimeError("Internal database password=SUPER_FAKE_PASSWORD_123 failed connection")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/test-unhandled")

    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert data["error"]["message"] == "An internal error occurred."
    assert "SUPER_FAKE_PASSWORD_123" not in response.text
    assert "RuntimeError" not in response.text


def test_exception_middleware_internal_message_isolation() -> None:
    """Verify internal_message attribute is omitted from public HTTP responses."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-internal-msg")
    def internal_msg_route() -> None:
        raise EntityNotFoundError(
            message="Resource not found.",
            internal_message="Secret database table account_db.internal was unreachable",
        )

    client = TestClient(test_app)
    response = client.get("/test-internal-msg")

    assert response.status_code == 404
    assert "account_db.internal" not in response.text


def test_exception_middleware_secret_sanitization_in_details() -> None:
    """Verify details dictionary with sensitive keys is sanitized in HTTP responses."""
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-secret-details")
    def secret_details_route() -> None:
        raise UseCaseError(
            message="Validation failed.",
            details={"field": "password", "password": "SUPER_FAKE_SECRET_PASS_123"},
        )

    client = TestClient(test_app)
    response = client.get("/test-secret-details")

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["details"]["password"] == "[REDACTED]"
    assert "SUPER_FAKE_SECRET_PASS_123" not in response.text


def test_fastapi_http_exception_compatibility() -> None:
    """Verify standard FastAPI HTTPException passes through cleanly."""
    test_app = create_app()

    @test_app.get("/test-http-exc")
    def http_exc_route() -> None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")

    client = TestClient(test_app)
    response = client.get("/test-http-exc")

    assert response.status_code == 401
    assert "Unauthorized access" in response.text
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_non_existent_route_404(client: TestClient) -> None:
    """Verify non-existent API routes return 404 status code."""
    response = client.get("/does-not-exist-route")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_method_not_allowed_405(client: TestClient) -> None:
    """Verify POST request to GET-only root endpoint returns 405 status code."""
    response = client.post("/")
    assert response.status_code == 405
    data = response.json()
    assert data["success"] is False


def test_exception_structured_logging_in_middleware(caplog: pytest.LogCaptureFixture) -> None:
    """Verify exception middleware logs structured JSON events for application failures."""
    configure_logging()
    test_app = FastAPI()
    from app.exceptions.handler import register_exception_handlers
    from app.middleware.registration import register_middleware

    register_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/test-log-route")
    def log_route() -> None:
        raise EntityNotFoundError("Entity account_999 missing.")

    client = TestClient(test_app)
    with caplog.at_level(logging.INFO):
        response = client.get("/test-log-route")

    assert response.status_code == 404
    assert len(caplog.records) >= 1
    error_record = [r for r in caplog.records if r.name == "agentpay.middleware.exception"][0]

    assert getattr(error_record, "event", None) == "application.error"
    assert getattr(error_record, "error_code", None) == "RESOURCE_NOT_FOUND"
