"""Unit, integration, security, and performance tests for Phase 026 API Health Endpoint."""

import asyncio
import logging
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.logging import configure_logging
from app.main import create_app


def test_health_endpoint_returns_200_ok() -> None:
    """Verify GET /api/v1/health returns HTTP 200 OK status code."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_response_is_canonical_success_envelope() -> None:
    """Verify response is structured inside canonical SuccessResponse envelope."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    body = response.json()

    assert body["success"] is True
    assert "data" in body
    assert "meta" in body


def test_health_endpoint_status_is_healthy() -> None:
    """Verify data.status equals 'healthy'."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    data = response.json()["data"]

    assert data["status"] == "healthy"


def test_health_endpoint_generates_request_id_when_absent() -> None:
    """Verify request ID is generated in meta envelope when header is absent."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    req_id = response.json()["meta"]["request_id"]

    assert req_id is not None
    assert len(req_id) > 0


def test_health_endpoint_preserves_incoming_x_request_id() -> None:
    """Verify incoming X-Request-ID header is preserved in response header and meta."""
    app = create_app()
    client = TestClient(app)

    custom_id = "k8s-liveness-probe-check-999"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    assert response.json()["meta"]["request_id"] == custom_id


def test_health_endpoint_x_request_id_matches_meta_request_id() -> None:
    """Verify response header X-Request-ID matches meta.request_id exactly."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    header_id = response.headers.get("x-request-id")
    body_id = response.json()["meta"]["request_id"]

    assert header_id == body_id


def test_health_endpoint_no_authentication_required() -> None:
    """Verify liveness probe endpoint requires zero authentication tokens."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_performs_no_external_dependency_checks() -> None:
    """Verify health check returns healthy instantly without requiring external databases."""
    app = create_app()
    client = TestClient(app)

    start_time = time.perf_counter()
    response = client.get("/api/v1/health")
    duration = time.perf_counter() - start_time

    assert response.status_code == 200
    assert duration < 0.1  # Fast execution (< 100ms)


def test_health_endpoint_no_query_string_leakage() -> None:
    """Verify query strings do not leak into response payload."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health?token=SUPER_SECRET_TOKEN_999")
    assert response.status_code == 200
    assert "SUPER_SECRET_TOKEN_999" not in response.text


def test_health_endpoint_does_not_expose_system_secrets_or_metadata() -> None:
    """Verify response excludes sensitive host, OS, PID, or credential metadata."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    text = response.text

    forbidden_terms = [
        "hostname",
        "process_id",
        "python_version",
        "os_version",
        "env",
        "password",
        "secret",
        "database",
        "redis",
    ]
    for term in forbidden_terms:
        assert term not in text.lower()


def test_openapi_contains_health_route(client: TestClient) -> None:
    """Verify /openapi.json documents /api/v1/health route."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "/api/v1/health" in schema["paths"]


def test_openapi_contains_get_operation_and_tags(client: TestClient) -> None:
    """Verify /openapi.json documents GET operation and Health tag."""
    response = client.get("/openapi.json")
    schema = response.json()

    health_path = schema["paths"]["/api/v1/health"]
    assert "get" in health_path
    assert "Health" in health_path["get"]["tags"]


def test_openapi_documents_200_response_schema(client: TestClient) -> None:
    """Verify /openapi.json documents HTTP 200 response schema for health check."""
    response = client.get("/openapi.json")
    schema = response.json()

    get_op = schema["paths"]["/api/v1/health"]["get"]
    assert "200" in get_op["responses"]


def test_health_endpoint_cors_compatibility() -> None:
    """Verify CORS preflight and headers apply cleanly to health endpoint."""
    app = create_app()
    client = TestClient(app)

    headers = {"Origin": "http://localhost:3000"}
    response = client.get("/api/v1/health", headers=headers)

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_health_endpoint_structured_logging_compatibility(caplog: pytest.LogCaptureFixture) -> None:
    """Verify API middleware logs structured lifecycle event for health request."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    rec = api_records[-1]
    assert getattr(rec, "path", None) == "/api/v1/health"
    assert getattr(rec, "status_code", None) == 200


def test_health_endpoint_repeated_invocations() -> None:
    """Verify health endpoint can be invoked repeatedly without state degradation."""
    app = create_app()
    client = TestClient(app)

    for _ in range(10):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_concurrent_health_requests_maintain_request_id_isolation() -> None:
    """Verify concurrent health requests maintain distinct request ID isolation."""
    app = create_app()
    client = TestClient(app)

    def send_health(n: int) -> dict[str, Any]:
        res = client.get("/api/v1/health", headers={"X-Request-ID": f"k8s-probe-{n}"})
        return res.json()  # type: ignore[no-any-return]

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, send_health, i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    for i in range(10):
        assert results[i]["success"] is True
        assert results[i]["meta"]["request_id"] == f"k8s-probe-{i}"


def test_unsupported_http_methods_return_405() -> None:
    """Verify POST, PUT, DELETE to /api/v1/health return 405 Method Not Allowed."""
    app = create_app()
    client = TestClient(app)

    for method in ["post", "put", "delete", "patch"]:
        res = getattr(client, method)("/api/v1/health")
        assert res.status_code == 405
        assert res.json()["success"] is False


def test_no_duplicate_health_routes_in_app() -> None:
    """Audit application route table to verify no duplicate health routes exist."""
    app = create_app()
    openapi_paths = app.openapi().get("paths", {})
    health_occurrences = [p for p in openapi_paths if p.endswith("/health")]
    assert len(health_occurrences) == 1












def test_performance_lightweight_execution() -> None:
    """Verify health endpoint execution introduces negligible overhead."""
    app = create_app()
    client = TestClient(app)

    start = time.perf_counter()
    for _ in range(50):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
    total_duration = time.perf_counter() - start

    assert total_duration < 1.0  # 50 requests in under 1 second
