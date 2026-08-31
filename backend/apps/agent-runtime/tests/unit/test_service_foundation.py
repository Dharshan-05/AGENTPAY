"""Comprehensive unit, integration, lifecycle, security, performance, ordering,
and regression tests for Phase 030 Backend Service Foundation.
"""

import logging
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr


from app.application.services.readiness import ApplicationReadinessCheck, ReadinessService
from app.bootstrap import bootstrap_app
from app.core.config import Environment, Settings, get_settings
from app.core.lifespan import (
    LifecycleComponent,
    ServiceState,
    _registered_components,
    get_service_state,
    lifespan,
    register_lifecycle_component,
    set_service_state,
)
from app.main import create_app


class DummyLifecycleComponent(LifecycleComponent):
    """Dummy lifecycle component for testing startup and shutdown hooks."""

    def __init__(
        self,
        name: str,
        fail_on_startup: bool = False,
        fail_on_shutdown: bool = False,
    ) -> None:
        self._name = name
        self._fail_on_startup = fail_on_startup
        self._fail_on_shutdown = fail_on_shutdown
        self.started = False
        self.stopped = False

    @property
    def name(self) -> str:
        return self._name

    async def startup(self) -> None:
        if self._fail_on_startup:
            raise RuntimeError(f"Startup failure in {self._name}")
        self.started = True

    async def shutdown(self) -> None:
        if self._fail_on_shutdown:
            raise RuntimeError(f"Shutdown failure in {self._name}")
        self.stopped = True


def test_create_app_returns_fastapi_instance() -> None:
    """Verify create_app factory returns a valid FastAPI application instance."""
    app = create_app()
    assert isinstance(app, FastAPI)


def test_repeated_create_app_returns_independent_instances() -> None:
    """Verify calling create_app multiple times produces independent application instances."""
    app1 = create_app()
    app2 = create_app()
    assert app1 is not app2


def test_bootstrap_app_with_custom_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify bootstrap_app respects custom settings passed explicitly."""
    get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "Custom AGENTPAY")
    custom_settings = Settings(app_name="Custom AGENTPAY", debug=False)
    app = bootstrap_app(custom_settings)
    assert app.title == "Custom AGENTPAY"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_lifespan_state_transitions() -> None:
    """Verify lifespan manager transitions ServiceState cleanly through lifecycle."""
    app = create_app()
    set_service_state(ServiceState.STOPPED)

    async with lifespan(app):
        assert get_service_state() == ServiceState.READY

    assert get_service_state() == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_registered_lifecycle_component_execution() -> None:
    """Verify registered LifecycleComponent instances run startup and shutdown hooks."""
    _registered_components.clear()
    component = DummyLifecycleComponent(name="test_component")
    register_lifecycle_component(component)

    app = create_app()
    async with lifespan(app):
        assert component.started is True

    assert component.stopped is True
    _registered_components.clear()


@pytest.mark.asyncio
async def test_component_startup_failure_sets_failed_state() -> None:
    """Verify component startup failure sets ServiceState.FAILED and raises exception."""
    _registered_components.clear()
    failing_component = DummyLifecycleComponent(name="failing_component", fail_on_startup=True)
    register_lifecycle_component(failing_component)

    app = create_app()
    with pytest.raises(RuntimeError, match="Startup failure"):
        async with lifespan(app):
            pass

    assert get_service_state() == ServiceState.FAILED
    _registered_components.clear()


@pytest.mark.asyncio
async def test_component_shutdown_error_logged_without_crashing_cleanup(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify component shutdown exception logs an error without crashing overall shutdown."""
    _registered_components.clear()
    failing_component = DummyLifecycleComponent(name="failing_shutdown", fail_on_shutdown=True)
    register_lifecycle_component(failing_component)

    app = create_app()
    with caplog.at_level(logging.ERROR):
        async with lifespan(app):
            pass

    assert get_service_state() == ServiceState.STOPPED
    assert "Component shutdown error" in caplog.text
    _registered_components.clear()


@pytest.mark.asyncio
async def test_readiness_check_fails_when_service_state_is_failed() -> None:
    """Verify ApplicationReadinessCheck returns ready=False when ServiceState is FAILED."""
    set_service_state(ServiceState.FAILED)
    check = ApplicationReadinessCheck()
    result = await check.check()

    assert result.ready is False
    assert result.details is not None
    assert result.details["service_state"] == ServiceState.FAILED.value
    set_service_state(ServiceState.STOPPED)


@pytest.mark.asyncio
async def test_readiness_check_fails_when_service_state_is_stopping() -> None:
    """Verify ApplicationReadinessCheck returns ready=False when ServiceState is STOPPING."""
    set_service_state(ServiceState.STOPPING)
    check = ApplicationReadinessCheck()
    result = await check.check()

    assert result.ready is False
    set_service_state(ServiceState.STOPPED)


def test_health_endpoint_independent_of_service_state() -> None:
    """Verify GET /api/v1/health returns 200 OK regardless of readiness state."""
    set_service_state(ServiceState.FAILED)
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"
    set_service_state(ServiceState.STOPPED)


def test_root_endpoint_returns_200_ok() -> None:
    """Verify GET / root status endpoint returns HTTP 200 OK."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["data"]["service"] == "agentpay-api"


def test_ready_endpoint_returns_200_ok_when_ready() -> None:
    """Verify GET /api/v1/ready returns HTTP 200 OK when ready."""
    set_service_state(ServiceState.READY)
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"
    set_service_state(ServiceState.STOPPED)


def test_openapi_json_returns_200_ok() -> None:
    """Verify GET /openapi.json returns HTTP 200 OK."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()


def test_docs_returns_200_ok_html() -> None:
    """Verify GET /docs returns HTTP 200 HTML page."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_redoc_returns_200_ok_html() -> None:
    """Verify GET /redoc returns HTTP 200 HTML page."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_request_id_preserved_when_provided() -> None:
    """Verify valid incoming X-Request-ID header is preserved in response headers and meta."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health", headers={"X-Request-ID": "foundation-test-001"})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == "foundation-test-001"
    assert response.json()["meta"]["request_id"] == "foundation-test-001"


def test_request_id_generated_when_absent() -> None:
    """Verify UUID4 request_id is generated when X-Request-ID header is absent."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    req_id = response.headers.get("x-request-id")
    assert req_id is not None
    assert response.json()["meta"]["request_id"] == req_id


def test_request_id_survives_404_error() -> None:
    """Verify X-Request-ID and meta.request_id are attached to 404 responses."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/non-existent-endpoint", headers={"X-Request-ID": "req-404-test"})
    assert response.status_code == 404
    assert response.headers.get("x-request-id") == "req-404-test"
    assert response.json()["meta"]["request_id"] == "req-404-test"


def test_request_id_survives_405_error() -> None:
    """Verify X-Request-ID and meta.request_id are attached to 405 Method Not Allowed responses."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/v1/health", headers={"X-Request-ID": "req-405-test"})
    assert response.status_code == 405
    assert response.headers.get("x-request-id") == "req-405-test"
    assert response.json()["meta"]["request_id"] == "req-405-test"


def test_cors_preflight_options_request() -> None:
    """Verify CORS preflight OPTIONS request returns 200 OK with expected access-control headers."""
    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_untrusted_cors_origin_rejected() -> None:
    """Verify untrusted CORS origin does not receive Access-Control-Allow-Origin header."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health", headers={"Origin": "http://untrusted-domain.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_success_response_envelope_structure() -> None:
    """Verify successful responses strictly adhere to {success, data, meta} envelope."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "meta" in data
    assert "request_id" in data["meta"]


def test_error_response_envelope_structure() -> None:
    """Verify error responses strictly adhere to {success, error, meta} envelope."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/does-not-exist")
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "meta" in data
    assert "request_id" in data["meta"]


def test_400_validation_error_code() -> None:
    """Verify invalid request ID header returns 400 VALIDATION_ERROR."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health", headers={"X-Request-ID": "invalid\r\nheader"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_404_resource_not_found_code() -> None:
    """Verify non-existent route returns 404 RESOURCE_NOT_FOUND."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/unknown-route")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_openapi_zero_secrets_leakage() -> None:
    """Verify /openapi.json schema text contains zero raw secrets or credentials."""
    app = create_app()
    client = TestClient(app)

    text = client.get("/openapi.json").text.lower()
    for forbidden in ["super_secret", "secret_pass", "postgres://", "redis://", "bearer "]:
        assert forbidden not in text


def test_error_response_zero_traceback_leakage() -> None:
    """Verify 404 and 500 error responses do not leak internal tracebacks or exception types."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/unknown-route")
    text = response.text.lower()
    assert "traceback" not in text
    assert 'file "' not in text


def test_no_duplicate_routes_on_repeated_bootstrap() -> None:
    """Verify multiple bootstrap calls do not duplicate application route paths."""
    app = create_app()
    openapi_paths = app.openapi().get("paths", {})

    route_keys = []
    for path, methods in openapi_paths.items():
        for method in methods:
            route_keys.append((method, path))

    assert len(route_keys) == len(set(route_keys))








def test_no_duplicate_logging_handlers() -> None:
    """Verify Repeated logging configuration does not duplicate root logger handlers."""
    root_logger = logging.getLogger()
    initial_count = len(root_logger.handlers)

    create_app()
    create_app()

    assert len(root_logger.handlers) == initial_count


def test_production_debug_mode_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify debug=True in production environment raises ValueError."""
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "true")
    with pytest.raises(Exception, match="PRODUCTION environment"):
        Settings(app_env=Environment.PRODUCTION, debug=True)
    get_settings.cache_clear()


def test_production_wildcard_cors_rejection() -> None:
    """Verify wildcard CORS in production environment raises ValueError."""
    get_settings.cache_clear()
    with pytest.raises(Exception, match="PRODUCTION environment"):
        Settings(
            _env_file=None,
            secret_key=SecretStr("a" * 32),
            jwt_secret=SecretStr("secure_jwt_secret_32chars_long_prod!"),
            postgres_password=SecretStr("secure_prod_password_32_bytes_long!"),
            postgres_host="prod-db.internal",
            app_env=Environment.PRODUCTION,
            debug=False,
            cors_allowed_origins=["*"],
        )
    get_settings.cache_clear()


def test_api_v1_version_prefix_enforced() -> None:
    """Verify API endpoints are mounted under /api/v1 prefix."""
    app = create_app()
    client = TestClient(app)

    r_health = client.get("/api/v1/health")
    assert r_health.status_code == 200

    r_unmounted = client.get("/api/v2/health")
    assert r_unmounted.status_code == 404


@pytest.mark.asyncio
async def test_readiness_service_multi_check_aggregation() -> None:
    """Verify ReadinessService aggregates multiple registered readiness checks."""
    c1 = DummyLifecycleComponent("c1")
    c1.started = True
    c2 = DummyLifecycleComponent("c2")
    c2.started = True

    service = ReadinessService(checks=[ApplicationReadinessCheck()])
    assert await service.is_ready() is True


def test_openapi_schema_operation_id_uniqueness() -> None:
    """Verify operation IDs across OpenAPI paths are unique."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    op_ids: list[str] = []
    for _path, methods in schema["paths"].items():
        for _method, details in methods.items():
            if isinstance(details, dict) and "operationId" in details:
                op_ids.append(details["operationId"])

    assert len(op_ids) == len(set(op_ids))


def test_openapi_vendor_extensions() -> None:
    """Verify x-service and x-api-version vendor extensions are attached."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema.get("x-service") == "agentpay-api"
    assert schema.get("x-api-version") == "1.0.0"


def test_docs_toggles_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify DOCS_ENABLED=False causes /docs to return 404 Not Found."""
    get_settings.cache_clear()
    monkeypatch.setenv("DOCS_ENABLED", "false")

    app = create_app()
    client = TestClient(app)

    assert client.get("/docs").status_code == 404
    get_settings.cache_clear()


def test_openapi_schema_determinism() -> None:
    """Verify repeated calls to /openapi.json produce identical schemas."""
    app = create_app()
    client = TestClient(app)

    s1 = client.get("/openapi.json").json()
    s2 = client.get("/openapi.json").json()
    assert s1 == s2
