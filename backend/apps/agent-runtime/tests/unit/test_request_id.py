"""Unit, integration, and security tests for Phase 024 Request ID Middleware."""

import asyncio
import uuid

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from app.core.logging import configure_logging
from app.domain.exceptions import EntityNotFoundError
from app.main import create_app


def is_valid_uuid4(val: str) -> bool:
    """Helper verifying string is a valid UUID4 representation."""
    try:
        parsed = uuid.UUID(val, version=4)
        return str(parsed) == val
    except ValueError:
        return False


def test_generates_uuid4_request_id_when_header_absent() -> None:
    """Verify request ID is generated as valid UUID4 when X-Request-ID header is missing."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    req_id = response.headers.get("x-request-id")
    assert req_id is not None
    assert is_valid_uuid4(req_id)


def test_preserves_valid_incoming_x_request_id() -> None:
    """Verify valid incoming X-Request-ID header is preserved in state and response."""
    test_app = create_app()

    @test_app.get("/test-id-state")
    def state_route(request: Request) -> dict[str, str]:
        return {"state_id": getattr(request.state, "request_id", "")}

    client = TestClient(test_app)
    custom_id = "test-correlation-123.456_789"
    response = client.get("/test-id-state", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    assert response.json()["data"]["state_id"] == custom_id


def test_request_id_identical_in_state_header_and_log(caplog: pytest.LogCaptureFixture) -> None:
    """Verify request ID is identical in state, response header, and http.request structured log."""
    configure_logging()
    app = create_app()

    client = TestClient(app)
    custom_id = "ident-check-id-99"
    response = client.get("/", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    assert getattr(api_records[-1], "request_id", None) == custom_id


def test_different_requests_receive_different_generated_ids() -> None:
    """Verify separate requests without headers receive distinct generated UUIDs."""
    app = create_app()
    client = TestClient(app)

    r1 = client.get("/")
    r2 = client.get("/")

    id1 = r1.headers.get("x-request-id")
    id2 = r2.headers.get("x-request-id")

    assert id1 != id2
    assert is_valid_uuid4(id1 or "")
    assert is_valid_uuid4(id2 or "")


def test_rejects_empty_request_id() -> None:
    """Verify empty string X-Request-ID generates a fresh valid UUID4."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/", headers={"X-Request-ID": ""})
    assert response.status_code == 200
    req_id = response.headers.get("x-request-id")
    assert req_id is not None
    assert is_valid_uuid4(req_id)


def test_rejects_whitespace_request_id() -> None:
    """Verify whitespace-only X-Request-ID generates a fresh valid UUID4."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/", headers={"X-Request-ID": "   "})
    assert response.status_code == 200
    req_id = response.headers.get("x-request-id")
    assert req_id is not None
    assert is_valid_uuid4(req_id)


def test_rejects_crlf_header_injection() -> None:
    """Verify CRLF header injection payload is rejected with 400 VALIDATION_ERROR."""
    app = create_app()
    client = TestClient(app)

    malicious_id = "abc\r\nInjected: true"
    response = client.get("/", headers={"X-Request-ID": malicious_id})

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Invalid request ID."
    assert "Injected" not in response.headers


def test_rejects_control_characters() -> None:
    """Verify request IDs containing control characters (\t, \n) return 400 VALIDATION_ERROR."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/", headers={"X-Request-ID": "bad\tID\n"})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_rejects_request_id_longer_than_128_chars() -> None:
    """Verify request ID exceeding 128 characters returns 400 VALIDATION_ERROR."""
    app = create_app()
    client = TestClient(app)

    long_id = "a" * 129
    response = client.get("/", headers={"X-Request-ID": long_id})

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_rejects_unsafe_characters() -> None:
    """Verify malicious script and path traversal chars in X-Request-ID are rejected."""
    app = create_app()
    client = TestClient(app)

    for unsafe in ["<script>alert(1)</script>", "../../etc/passwd", "DROP TABLE users;"]:
        response = client.get("/", headers={"X-Request-ID": unsafe})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_does_not_echo_invalid_request_id() -> None:
    """Verify raw invalid request ID is never echoed back in response body or headers."""
    app = create_app()
    client = TestClient(app)

    malicious = "ECHO_SECRET_ATTEMPT_99\r\nHeader: Bad"
    response = client.get("/", headers={"X-Request-ID": malicious})

    assert response.status_code == 400
    assert malicious not in response.text
    assert "ECHO_SECRET_ATTEMPT_99" not in response.text


def test_404_response_contains_request_id() -> None:
    """Verify 404 Not Found responses carry X-Request-ID header."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.headers.get("x-request-id") is not None


def test_405_response_contains_request_id() -> None:
    """Verify 405 Method Not Allowed responses carry X-Request-ID header."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/")  # Root supports GET only
    assert response.status_code == 405
    assert response.headers.get("x-request-id") is not None


def test_fastapi_http_exception_contains_request_id() -> None:
    """Verify FastAPI HTTPException responses carry X-Request-ID header."""
    test_app = create_app()

    @test_app.get("/test-http-exc")
    def exc_route() -> None:
        raise HTTPException(status_code=403, detail="Access denied")

    client = TestClient(test_app)
    response = client.get("/test-http-exc", headers={"X-Request-ID": "exc-id-100"})
    assert response.status_code == 403
    assert response.headers.get("x-request-id") == "exc-id-100"


def test_agentpay_error_response_contains_request_id() -> None:
    """Verify AgentPayError responses carry X-Request-ID header."""
    test_app = create_app()

    @test_app.get("/test-domain-exc")
    def domain_exc_route() -> None:
        raise EntityNotFoundError("Entity not found")

    client = TestClient(test_app)
    response = client.get("/test-domain-exc", headers={"X-Request-ID": "domain-id-200"})
    assert response.status_code == 404
    assert response.headers.get("x-request-id") == "domain-id-200"


def test_unhandled_500_response_contains_request_id() -> None:
    """Verify unhandled Exception 500 responses carry X-Request-ID header."""
    test_app = create_app()

    @test_app.get("/test-500-exc")
    def fatal_route() -> None:
        raise RuntimeError("Fatal system failure")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/test-500-exc", headers={"X-Request-ID": "fatal-id-500"})
    assert response.status_code == 500
    assert response.headers.get("x-request-id") == "fatal-id-500"


def test_error_logs_contain_request_id(caplog: pytest.LogCaptureFixture) -> None:
    """Verify exception logs contain request_id in extra context."""
    configure_logging()
    test_app = create_app()

    @test_app.get("/test-log-err")
    def log_err_route() -> None:
        raise EntityNotFoundError("Entity missing")

    client = TestClient(test_app)
    response = client.get("/test-log-err", headers={"X-Request-ID": "log-err-777"})
    assert response.status_code == 404

    exc_records = [r for r in caplog.records if r.name == "agentpay.middleware.exception"]
    assert len(exc_records) >= 1
    assert getattr(exc_records[-1], "request_id", None) == "log-err-777"


def test_secret_protection_in_logging_with_request_id(caplog: pytest.LogCaptureFixture) -> None:
    """Verify query strings, Authorization headers, and bodies remain unlogged with request ID."""
    configure_logging()
    app = create_app()
    client = TestClient(app)

    secret_auth = "Bearer SUPER_SECRET_TOKEN_999"
    response = client.get(
        "/?token=SECRET_QUERY_VAL",
        headers={
            "X-Request-ID": "req-sec-123",
            "Authorization": secret_auth,
        },
    )
    assert response.status_code == 200

    api_records = [r for r in caplog.records if r.name == "agentpay.middleware.api"]
    assert len(api_records) >= 1
    rec = api_records[-1]
    assert getattr(rec, "request_id", None) == "req-sec-123"
    log_msg = rec.getMessage()
    assert "SECRET_QUERY_VAL" not in log_msg
    assert secret_auth not in log_msg


def test_cors_preflight_preserves_request_id() -> None:
    """Verify CORS preflight OPTIONS request returns X-Request-ID."""
    app = create_app()
    client = TestClient(app)

    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Request-ID, Content-Type",
        "X-Request-ID": "cors-preflight-id-1",
    }
    response = client.options("/api/v1", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == "cors-preflight-id-1"


def test_repeated_app_creation_no_duplicate_middleware() -> None:
    """Verify multiple create_app() invocations run idempotently without duplicating headers."""
    app1 = create_app()
    app2 = create_app()

    client1 = TestClient(app1)
    client2 = TestClient(app2)

    r1 = client1.get("/", headers={"X-Request-ID": "id-app-1"})
    r2 = client2.get("/", headers={"X-Request-ID": "id-app-2"})

    assert r1.headers.get("x-request-id") == "id-app-1"
    assert r2.headers.get("x-request-id") == "id-app-2"


@pytest.mark.asyncio
async def test_concurrent_requests_do_not_share_request_ids() -> None:
    """Verify concurrent requests do not cross-contaminate request state IDs."""
    app = create_app()
    client = TestClient(app)

    def send_req(n: int) -> str:
        req_id = f"concurrent-req-id-{n}"
        res = client.get("/", headers={"X-Request-ID": req_id})
        return str(res.headers.get("x-request-id"))

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, send_req, i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    for i in range(10):
        assert results[i] == f"concurrent-req-id-{i}"


def test_openapi_schema_unaffected() -> None:
    """Verify /openapi.json continues returning 200 OK with OpenAPI contract."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers.get("x-request-id") is not None
    assert response.json()["info"]["title"] == "AGENTPAY API"
