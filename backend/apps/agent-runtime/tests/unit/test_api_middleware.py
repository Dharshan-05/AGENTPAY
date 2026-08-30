"""Unit and integration tests for Phase 021 API Middleware and request lifecycle timing."""

import logging
import time

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.core.logging import configure_logging
from app.domain.exceptions import EntityNotFoundError
from app.main import create_app


def test_api_middleware_request_timing_and_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify APIMiddleware logs structured http.request event with duration_ms >= 0."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/")

    assert response.status_code == 200

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1

    record = api_records[-1]
    assert getattr(record, "event", None) == "http.request"
    assert getattr(record, "method", None) == "GET"
    assert getattr(record, "path", None) == "/"
    assert getattr(record, "status_code", None) == 200
    assert isinstance(getattr(record, "duration_ms", None), float)
    assert getattr(record, "duration_ms", -1) >= 0.0


def test_query_string_secret_protection(caplog: pytest.LogCaptureFixture) -> None:
    """Verify query strings containing sensitive parameters are omitted from path logs."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/?token=SUPER_FAKE_TOKEN_123&password=SUPER_FAKE_PASS_456")

    assert response.status_code == 200

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "path", None) == "/"
    for r in api_records:
        msg = r.getMessage()
        assert "SUPER_FAKE_TOKEN_123" not in msg
        assert "SUPER_FAKE_PASS_456" not in msg


def test_header_and_body_secret_protection(caplog: pytest.LogCaptureFixture) -> None:
    """Verify headers, cookies, and request bodies are omitted from middleware logs."""
    configure_logging()
    test_app = FastAPI()
    from app.middleware.registration import register_middleware

    register_middleware(test_app)

    @test_app.post("/test-secret-body")
    def secret_body_route() -> dict[str, str]:
        return {"status": "ok", "secret_response": "SUPER_FAKE_RESPONSE_SECRET_789"}

    client = TestClient(test_app)
    headers = {
        "Authorization": "Bearer SUPER_FAKE_JWT_TOKEN_999",
        "Cookie": "session=SUPER_FAKE_SESSION_888",
    }
    payload = {"password": "SUPER_FAKE_INPUT_PASS_777"}

    with caplog.at_level(logging.INFO):
        response = client.post("/test-secret-body", json=payload, headers=headers)

    assert response.status_code == 200

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1

    for r in api_records:
        msg = r.getMessage()
        assert "SUPER_FAKE_JWT_TOKEN_999" not in msg
        assert "SUPER_FAKE_SESSION_888" not in msg
        assert "SUPER_FAKE_INPUT_PASS_777" not in msg
        assert "SUPER_FAKE_RESPONSE_SECRET_789" not in msg


def test_exception_propagation_and_timing_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify AgentPayError exceptions translate to 404 and APIMiddleware logs timing."""

    configure_logging()
    test_app = create_app()

    @test_app.get("/test-err-route")
    def err_route() -> None:
        raise EntityNotFoundError("Target entity account_555 missing.")

    client = TestClient(test_app)

    with caplog.at_level(logging.INFO):
        response = client.get("/test-err-route")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "status_code", None) == 404
    assert getattr(record, "path", None) == "/test-err-route"


def test_unhandled_exception_timing_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify unhandled Exception translates to 500 and APIMiddleware captures status_code=500."""
    configure_logging()
    test_app = create_app()

    @test_app.get("/test-runtime-err")
    def runtime_err_route() -> None:
        raise RuntimeError("Unexpected failure")

    client = TestClient(test_app, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO):
        response = client.get("/test-runtime-err")

    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "INTERNAL_ERROR"

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "status_code", None) == 500


def test_fastapi_http_exception_timing_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify standard HTTPException(401) captures status_code=401 in APIMiddleware."""
    configure_logging()
    test_app = create_app()

    @test_app.get("/test-401")
    def unauthorized_route() -> None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    client = TestClient(test_app)

    with caplog.at_level(logging.INFO):
        response = client.get("/test-401")

    assert response.status_code == 401

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "status_code", None) == 401


def test_non_existent_route_404_timing(caplog: pytest.LogCaptureFixture) -> None:
    """Verify non-existent routes capture status_code=404 in APIMiddleware."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/does-not-exist-route")

    assert response.status_code == 404

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "status_code", None) == 404


def test_method_not_allowed_405_timing(caplog: pytest.LogCaptureFixture) -> None:
    """Verify POST request to GET-only route captures status_code=405 in APIMiddleware."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.post("/")

    assert response.status_code == 405

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    assert getattr(record, "status_code", None) == 405


def test_slow_request_duration_timing(caplog: pytest.LogCaptureFixture) -> None:
    """Verify processing duration is accurately measured in milliseconds."""
    configure_logging()
    test_app = create_app()

    @test_app.get("/test-sleep")
    def sleep_route() -> dict[str, str]:
        time.sleep(0.05)
        return {"status": "slept"}

    client = TestClient(test_app)

    with caplog.at_level(logging.INFO):
        response = client.get("/test-sleep")

    assert response.status_code == 200

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    record = api_records[-1]

    duration = getattr(record, "duration_ms", 0.0)
    assert duration >= 40.0


def test_repeated_app_creation_no_duplicate_middleware() -> None:
    """Verify repeated app creation builds independent applications cleanly."""
    app1 = create_app()
    app2 = create_app()

    client1 = TestClient(app1)
    client2 = TestClient(app2)

    assert client1.get("/").status_code == 200
    assert client2.get("/").status_code == 200
