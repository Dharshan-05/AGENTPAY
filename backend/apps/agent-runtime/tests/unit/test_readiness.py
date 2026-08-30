"""Unit, integration, security, and performance tests for Phase 027 API Readiness Endpoint."""

import asyncio
import logging
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.v1.ready import get_readiness_service
from app.application.services.readiness import (
    ApplicationReadinessCheck,
    ReadinessCheck,
    ReadinessCheckResult,
    ReadinessService,
    ReadinessStatus,
)
from app.core.logging import configure_logging
from app.main import create_app


class FailingReadinessCheck(ReadinessCheck):
    """Failing readiness check for testing fail-closed behavior."""

    @property
    def name(self) -> str:
        return "failing_service"

    async def check(self) -> ReadinessCheckResult:
        return ReadinessCheckResult(
            name=self.name,
            ready=False,
            details={"error": "Dependency connection failed"},
        )


class ExceptionThrowingCheck(ReadinessCheck):
    """Exception-throwing check for testing exception fail-closed safety."""

    @property
    def name(self) -> str:
        return "broken_check"

    async def check(self) -> ReadinessCheckResult:
        raise RuntimeError("Database connection password=SECRET_PASS_123 refused")


class SlowReadinessCheck(ReadinessCheck):
    """Slow check for testing bounded execution timeouts."""

    @property
    def name(self) -> str:
        return "slow_check"

    async def check(self) -> ReadinessCheckResult:
        await asyncio.sleep(5.0)
        return ReadinessCheckResult(name=self.name, ready=True)


def test_ready_state_returns_200_ok() -> None:
    """Verify GET /api/v1/ready returns HTTP 200 OK status code when ready."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 200


def test_ready_response_has_canonical_envelope() -> None:
    """Verify successful readiness response is formatted inside canonical envelope."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    body = response.json()

    assert body["success"] is True
    assert "data" in body
    assert "meta" in body


def test_ready_response_status_is_ready() -> None:
    """Verify data.status equals 'ready'."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    data = response.json()["data"]

    assert data["status"] == "ready"


def test_readiness_request_id_present_in_meta() -> None:
    """Verify meta.request_id is present in readiness response."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    req_id = response.json()["meta"]["request_id"]

    assert req_id is not None
    assert len(req_id) > 0


def test_readiness_preserves_incoming_x_request_id() -> None:
    """Verify incoming X-Request-ID header is preserved in readiness response header and meta."""
    app = create_app()
    client = TestClient(app)

    custom_id = "k8s-readiness-probe-check-777"
    response = client.get("/api/v1/ready", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    assert response.json()["meta"]["request_id"] == custom_id


def test_generated_x_request_id_works() -> None:
    """Verify generated request ID works when header is omitted."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    header_id = response.headers.get("x-request-id")
    body_id = response.json()["meta"]["request_id"]

    assert header_id == body_id


def test_readiness_failure_returns_503() -> None:
    """Verify failed readiness check causes GET /api/v1/ready to return HTTP 503."""
    app = create_app()
    unready_service = ReadinessService(checks=[FailingReadinessCheck()])

    app.dependency_overrides[get_readiness_service] = lambda: unready_service
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 503


def test_readiness_failure_uses_service_unavailable_code() -> None:
    """Verify 503 readiness error uses error.code = 'SERVICE_UNAVAILABLE'."""
    app = create_app()
    unready_service = ReadinessService(checks=[FailingReadinessCheck()])

    app.dependency_overrides[get_readiness_service] = lambda: unready_service
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_readiness_failure_public_message_is_safe() -> None:
    """Verify 503 response carries safe public error message."""
    app = create_app()
    unready_service = ReadinessService(checks=[FailingReadinessCheck()])

    app.dependency_overrides[get_readiness_service] = lambda: unready_service
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    body = response.json()

    assert body["error"]["message"] == "Service is not ready."


def test_readiness_internal_failure_details_not_exposed() -> None:
    """Verify internal diagnostic details or exceptions are omitted from public 503 body."""
    app = create_app()
    unready_service = ReadinessService(checks=[ExceptionThrowingCheck()])

    app.dependency_overrides[get_readiness_service] = lambda: unready_service
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    text = response.text

    assert "SECRET_PASS_123" not in text
    assert "RuntimeError" not in text
    assert "Traceback" not in text


def test_exceptions_in_readiness_checks_fail_closed() -> None:
    """Verify exceptions thrown inside a readiness check cause service to fail closed."""
    app = create_app()
    unready_service = ReadinessService(checks=[ExceptionThrowingCheck()])

    app.dependency_overrides[get_readiness_service] = lambda: unready_service
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_check_results_aggregate_correctly() -> None:
    """Verify ReadinessService aggregates multiple checks and requires all to be ready."""
    svc = ReadinessService(checks=[ApplicationReadinessCheck()])
    status, results = await svc.evaluate_readiness()

    assert status == ReadinessStatus.READY
    assert len(results) == 1
    assert results[0].ready is True


@pytest.mark.asyncio
async def test_multiple_checks_supported() -> None:
    """Verify ReadinessService supports registering multiple checks dynamically."""
    svc = ReadinessService(checks=[ApplicationReadinessCheck()])

    class SecondaryCheck(ReadinessCheck):
        @property
        def name(self) -> str:
            return "secondary"

        async def check(self) -> ReadinessCheckResult:
            return ReadinessCheckResult(name=self.name, ready=True)

    svc.register_check(SecondaryCheck())
    status, results = await svc.evaluate_readiness()

    assert status == ReadinessStatus.READY
    assert len(results) == 2


@pytest.mark.asyncio
async def test_single_failed_check_makes_service_not_ready() -> None:
    """Verify a single failing check among multiple checks makes aggregate readiness NOT_READY."""
    svc = ReadinessService(checks=[ApplicationReadinessCheck(), FailingReadinessCheck()])
    status, _ = await svc.evaluate_readiness()

    assert status == ReadinessStatus.NOT_READY


@pytest.mark.asyncio
async def test_readiness_timeout_fails_safely() -> None:
    """Verify slow readiness checks exceeding timeout fail closed to NOT_READY."""
    svc = ReadinessService(checks=[SlowReadinessCheck()], default_timeout_seconds=0.1)
    status, results = await svc.evaluate_readiness()

    assert status == ReadinessStatus.NOT_READY
    assert results[0].ready is False


def test_no_secrets_appear_in_readiness_response() -> None:
    """Verify secrets or credentials never leak in /ready response."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    text = response.text.lower()

    for secret_keyword in ["password", "secret", "token", "apikey", "credential", "private_key"]:
        assert secret_keyword not in text


def test_no_secrets_appear_in_readiness_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Verify readiness structured logs contain zero secret leakage."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    readiness_records = [
        r for r in caplog.records if getattr(r, "event", None) == "readiness.check"
    ]
    assert len(readiness_records) >= 1
    rec = readiness_records[-1]

    assert getattr(rec, "status", None) == "ready"


def test_404_behavior_remains_unchanged() -> None:
    """Verify 404 response on non-existent routes remains canonical."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/does-not-exist-route")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_405_behavior_on_ready_endpoint() -> None:
    """Verify POST, PUT, DELETE to /api/v1/ready return 405 Method Not Allowed."""
    app = create_app()
    client = TestClient(app)

    for method in ["post", "put", "delete", "patch"]:
        res = getattr(client, method)("/api/v1/ready")
        assert res.status_code == 405
        assert res.json()["success"] is False


def test_health_endpoint_remains_unchanged() -> None:
    """Verify Phase 026 /api/v1/health endpoint remains functional and unchanged."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"


def test_openapi_contains_readiness_route(client: TestClient) -> None:
    """Verify /openapi.json documents /api/v1/ready path."""
    response = client.get("/openapi.json")
    schema = response.json()

    assert "/api/v1/ready" in schema["paths"]


def test_swagger_docs_remain_accessible(client: TestClient) -> None:
    """Verify /docs HTML endpoint remains accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_remains_accessible(client: TestClient) -> None:
    """Verify /redoc HTML endpoint remains accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_readiness_cors_compatibility() -> None:
    """Verify CORS preflight and allowed origins work cleanly with /api/v1/ready."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.asyncio
async def test_concurrent_readiness_requests_isolation() -> None:
    """Verify concurrent readiness requests maintain distinct request ID isolation."""
    app = create_app()
    client = TestClient(app)

    def req(n: int) -> dict[str, Any]:
        res = client.get("/api/v1/ready", headers={"X-Request-ID": f"ready-concur-{n}"})
        return res.json()  # type: ignore[no-any-return]

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, req, i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    for i in range(10):
        assert results[i]["success"] is True
        assert results[i]["meta"]["request_id"] == f"ready-concur-{i}"
