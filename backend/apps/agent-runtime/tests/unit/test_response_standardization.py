"""Unit, integration, and security tests for Phase 025 Response Standardization."""

import asyncio
from typing import Any

import pytest
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.application.exceptions import ApplicationConflictError, UseCaseError
from app.domain.exceptions import EntityNotFoundError
from app.exceptions.config_exceptions import ConfigurationError
from app.infrastructure.exceptions import ExternalServiceError
from app.main import create_app
from app.schemas.common import ResponseMeta, SuccessResponse


def test_success_response_structure_has_success_data_meta() -> None:
    """Verify successful endpoint responses contain success=true, data, and meta envelopes."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/")
    assert res.status_code == 200
    body = res.json()

    assert body["success"] is True
    assert "data" in body
    assert "meta" in body
    assert body["data"]["service"] == "agentpay-api"


def test_meta_contains_request_id() -> None:
    """Verify response meta contains non-empty request_id."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert "request_id" in body["meta"]
    assert len(body["meta"]["request_id"]) > 0


def test_meta_request_id_equals_x_request_id_header() -> None:
    """Verify meta.request_id equals X-Request-ID HTTP response header."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/", headers={"X-Request-ID": "custom-req-id-100"})
    assert res.status_code == 200
    header_id = res.headers.get("x-request-id")
    body_id = res.json()["meta"]["request_id"]

    assert header_id == "custom-req-id-100"
    assert body_id == "custom-req-id-100"
    assert header_id == body_id


def test_meta_request_id_equals_request_state() -> None:
    """Verify meta.request_id equals request.state.request_id."""
    app = create_app()

    @app.get("/test-state-eq")
    def state_eq_route(request: Request) -> dict[str, str]:
        return {"state_id": getattr(request.state, "request_id", "")}

    client = TestClient(app)
    res = client.get("/test-state-eq", headers={"X-Request-ID": "state-req-id-200"})

    assert res.status_code == 200
    body = res.json()
    assert body["meta"]["request_id"] == "state-req-id-200"
    assert body["data"]["state_id"] == "state-req-id-200"


def test_null_success_data_remains_explicit() -> None:
    """Verify endpoints intentionally returning null data preserve explicit data=null."""
    app = create_app()

    @app.get("/test-null-data")
    def null_route() -> None:
        return None

    client = TestClient(app)
    res = client.get("/test-null-data")

    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"] is None
    assert "meta" in body


def test_201_created_response_standardized() -> None:
    """Verify 201 Created responses are wrapped into canonical SuccessResponse."""
    app = create_app()

    @app.post("/test-201", status_code=201)
    def created_route() -> dict[str, str]:
        return {"id": "res_123"}

    client = TestClient(app)
    res = client.post("/test-201")

    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["id"] == "res_123"


def test_202_accepted_response_standardized() -> None:
    """Verify 202 Accepted responses are wrapped into canonical SuccessResponse."""
    app = create_app()

    @app.post("/test-202", status_code=202)
    def accepted_route() -> dict[str, str]:
        return {"status": "queued"}

    client = TestClient(app)
    res = client.post("/test-202")

    assert res.status_code == 202
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "queued"


def test_204_no_content_remains_bodyless() -> None:
    """Verify HTTP 204 No Content responses remain completely bodyless with X-Request-ID header."""
    app = create_app()

    @app.delete("/test-204", status_code=204)
    def no_content_route() -> Response:
        return Response(status_code=204)

    client = TestClient(app)
    res = client.delete("/test-204", headers={"X-Request-ID": "no-content-id-204"})

    assert res.status_code == 204
    assert res.content == b""
    assert res.headers.get("x-request-id") == "no-content-id-204"


def test_400_validation_error_standardized() -> None:
    """Verify 400 validation error responses carry canonical error contract."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/?token=invalid", headers={"X-Request-ID": "bad\tID\n"})
    assert res.status_code == 400
    body = res.json()

    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Invalid request ID."
    assert body["meta"]["request_id"] is not None


def test_404_error_standardized() -> None:
    """Verify 404 Not Found responses carry canonical ErrorResponse structure."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/does-not-exist-route", headers={"X-Request-ID": "err-404-id"})
    assert res.status_code == 404
    body = res.json()

    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert body["meta"]["request_id"] == "err-404-id"


def test_405_error_standardized() -> None:
    """Verify 405 Method Not Allowed responses carry canonical ErrorResponse structure."""
    app = create_app()
    client = TestClient(app)

    res = client.post("/", headers={"X-Request-ID": "err-405-id"})
    assert res.status_code == 405
    body = res.json()

    assert body["success"] is False
    assert body["meta"]["request_id"] == "err-405-id"


def test_409_conflict_error_standardized() -> None:
    """Verify 409 Conflict error responses carry canonical error contract."""
    app = create_app()

    @app.get("/test-409")
    def conflict_route() -> None:
        raise ApplicationConflictError("Duplicate resource key")

    client = TestClient(app)
    res = client.get("/test-409")

    assert res.status_code == 409
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_CONFLICT"
    assert body["error"]["message"] == "Duplicate resource key"


def test_401_unauthorized_error_standardized() -> None:
    """Verify 401 Unauthorized error responses carry canonical error contract."""
    app = create_app()

    @app.get("/test-401")
    def unauth_route() -> None:
        raise HTTPException(status_code=401, detail="Token expired")

    client = TestClient(app)
    res = client.get("/test-401")

    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"] == "Token expired"


def test_403_forbidden_error_standardized() -> None:
    """Verify 403 Forbidden error responses carry canonical error contract."""
    app = create_app()

    @app.get("/test-403")
    def forbidden_route() -> None:
        raise HTTPException(status_code=403, detail="Forbidden action")

    client = TestClient(app)
    res = client.get("/test-403")

    assert res.status_code == 403
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"
    assert body["error"]["message"] == "Forbidden action"


def test_500_internal_error_standardized() -> None:
    """Verify 500 Configuration error responses carry canonical error contract."""
    app = create_app()

    @app.get("/test-500")
    def cfg_route() -> None:
        raise ConfigurationError("Invalid DB setup")

    client = TestClient(app)
    res = client.get("/test-500")

    assert res.status_code == 500
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CONFIGURATION"


def test_503_service_unavailable_standardized() -> None:
    """Verify 503 External Service error responses carry canonical error contract."""
    app = create_app()

    @app.get("/test-503")
    def ext_route() -> None:
        raise ExternalServiceError("Payment gateway down")

    client = TestClient(app)
    res = client.get("/test-503")

    assert res.status_code == 503
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_agentpay_error_standardized() -> None:
    """Verify AgentPayError instances translate cleanly to ErrorResponse."""
    app = create_app()

    @app.get("/test-domain-err")
    def domain_route() -> None:
        raise EntityNotFoundError("Account 123 missing")

    client = TestClient(app)
    res = client.get("/test-domain-err")

    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert body["error"]["message"] == "Account 123 missing"


def test_http_exception_standardized() -> None:
    """Verify HTTPException instances translate cleanly to ErrorResponse."""
    app = create_app()

    @app.get("/test-http-err")
    def http_route() -> None:
        raise HTTPException(status_code=400, detail="Malformed parameters")

    client = TestClient(app)
    res = client.get("/test-http-err")

    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Malformed parameters"


def test_request_validation_error_standardized() -> None:
    """Verify validation errors translate cleanly to ErrorResponse with details."""
    app = create_app()

    @app.post("/test-val-err")
    def val_route(body_dict: dict[str, int]) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    res = client.post("/test-val-err", json={"invalid": "type"})

    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in body["error"]


def test_malformed_json_syntax_error_standardized() -> None:
    """Verify malformed JSON syntax error translates cleanly to ErrorResponse."""
    app = create_app()

    @app.post("/test-json-syntax")
    def json_route(payload: dict[str, Any]) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    res = client.post(
        "/test-json-syntax",
        content="{bad_json",
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_unhandled_exception_standardized() -> None:
    """Verify unhandled Exception translates to safe generic 500 ErrorResponse."""
    app = create_app()

    @app.get("/test-unhandled")
    def fatal_route() -> None:
        raise RuntimeError("DB password=SUPER_SECRET_CONN_123 failed")

    client = TestClient(app, raise_server_exceptions=False)
    res = client.get("/test-unhandled")

    assert res.status_code == 500
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["message"] == "An internal error occurred."
    assert body["error"]["details"] is None


def test_internal_traceback_not_exposed() -> None:
    """Verify python tracebacks and file paths are never exposed in responses."""
    app = create_app()

    @app.get("/test-tb")
    def tb_route() -> None:
        raise RuntimeError("Traceback leakage check /app/infrastructure/db.py line 42")

    client = TestClient(app, raise_server_exceptions=False)
    res = client.get("/test-tb")

    assert res.status_code == 500
    assert "Traceback" not in res.text
    assert "/app/infrastructure/db.py" not in res.text


def test_internal_message_not_exposed() -> None:
    """Verify internal_message attribute of AgentPayError is omitted from public response."""
    app = create_app()

    @app.get("/test-internal-msg")
    def internal_route() -> None:
        raise EntityNotFoundError(
            message="Entity missing.",
            internal_message="DB table tbl_secrets_99 query failed",
        )

    client = TestClient(app)
    res = client.get("/test-internal-msg")

    assert res.status_code == 404
    assert "tbl_secrets_99" not in res.text


def test_secrets_not_exposed_in_error_details() -> None:
    """Verify sensitive parameters (password, token, api_key) are sanitized in error details."""
    app = create_app()

    @app.get("/test-secret-err")
    def secret_err_route() -> None:
        raise UseCaseError(
            message="Invalid parameters.",
            details={"password": "SUPER_SECRET_PASSWORD_123", "api_key": "SUPER_SECRET_KEY_456"},
        )

    client = TestClient(app)
    res = client.get("/test-secret-err")

    assert res.status_code == 400
    body = res.json()
    assert body["error"]["details"]["password"] == "[REDACTED]"
    assert body["error"]["details"]["api_key"] == "[REDACTED]"
    assert "SUPER_SECRET_PASSWORD_123" not in res.text
    assert "SUPER_SECRET_KEY_456" not in res.text


def test_request_id_preserved_on_errors() -> None:
    """Verify X-Request-ID header and meta.request_id match on error responses."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/does-not-exist", headers={"X-Request-ID": "err-req-id-777"})
    assert res.status_code == 404
    assert res.headers.get("x-request-id") == "err-req-id-777"
    assert res.json()["meta"]["request_id"] == "err-req-id-777"


def test_request_id_preserved_on_success() -> None:
    """Verify X-Request-ID header and meta.request_id match on success responses."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/", headers={"X-Request-ID": "succ-req-id-888"})
    assert res.status_code == 200
    assert res.headers.get("x-request-id") == "succ-req-id-888"
    assert res.json()["meta"]["request_id"] == "succ-req-id-888"


def test_cors_remains_functional() -> None:
    """Verify CORS headers are attached to standardized responses."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_options_preflight_remains_functional() -> None:
    """Verify OPTIONS preflight request works cleanly with allowed origins."""
    app = create_app()
    client = TestClient(app)

    res = client.options(
        "/api/v1",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Request-ID, Content-Type",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_openapi_remains_accessible_unwrapped() -> None:
    """Verify /openapi.json returns raw unwrapped OpenAPI JSON schema."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/openapi.json")
    assert res.status_code == 200
    body = res.json()
    assert "openapi" in body
    assert "success" not in body  # Must NOT be wrapped into SuccessResponse!


def test_swagger_remains_accessible_unwrapped() -> None:
    """Verify /docs returns raw HTML page without wrapping."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/docs")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "").lower()


def test_redoc_remains_accessible_unwrapped() -> None:
    """Verify /redoc returns raw HTML page without wrapping."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/redoc")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "").lower()


def test_head_semantics_remain_valid() -> None:
    """Verify HEAD requests receive empty body and valid headers."""
    app = create_app()

    @app.head("/test-head")
    def head_route() -> Response:
        return Response(status_code=200)

    client = TestClient(app)
    res = client.head("/test-head")
    assert res.status_code == 200
    assert res.content == b""
    assert res.headers.get("x-request-id") is not None


def test_api_versioning_remains_valid() -> None:
    """Verify versioned route endpoints follow standardized response format."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/api/v1")
    assert res.status_code in [200, 404]  # Unmounted endpoint returns 404 ErrorResponse
    body = res.json()
    assert "success" in body
    assert "meta" in body


def test_no_double_wrapping_occurs() -> None:
    """Verify returning explicit SuccessResponse or JSONResponse is not wrapped twice."""
    app = create_app()

    @app.get("/test-double")
    def double_route() -> SuccessResponse[dict[str, str]]:
        return SuccessResponse(
            success=True,
            data={"item": "value"},
            meta=ResponseMeta(request_id="explicit-id-123"),
        )

    client = TestClient(app)
    res = client.get("/test-double")

    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"] == {"item": "value"}
    assert "data" not in body["data"]  # No nested data.data double-wrap!


def test_already_standardized_error_not_wrapped_twice() -> None:
    """Verify error responses generated by exception handlers are not re-wrapped."""
    app = create_app()

    @app.get("/test-explicit-err")
    def explicit_err_route() -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": "Manual error", "details": None},
                "meta": {"request_id": "manual-id-1"},
            },
        )

    client = TestClient(app)
    res = client.get("/test-explicit-err")

    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["message"] == "Manual error"
    assert "error" not in body["error"]  # No double error nesting!


def test_repeated_create_app_no_duplicate_middleware() -> None:
    """Verify multiple create_app() calls produce clean independent middleware stacks."""
    app1 = create_app()
    app2 = create_app()

    c1 = TestClient(app1)
    c2 = TestClient(app2)

    r1 = c1.get("/")
    r2 = c2.get("/")

    assert r1.json()["success"] is True
    assert r2.json()["success"] is True


@pytest.mark.asyncio
async def test_concurrent_requests_independent_request_ids() -> None:
    """Verify concurrent requests receive independent request IDs in meta envelope."""
    app = create_app()
    client = TestClient(app)

    def req(n: int) -> dict[str, Any]:
        res = client.get("/", headers={"X-Request-ID": f"concur-id-{n}"})
        return res.json()  # type: ignore[no-any-return]

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, req, i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    for i in range(10):
        assert results[i]["success"] is True
        assert results[i]["meta"]["request_id"] == f"concur-id-{i}"
