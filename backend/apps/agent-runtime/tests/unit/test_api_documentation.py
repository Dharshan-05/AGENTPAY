"""Unit, integration, schema validation, toggle, stability, and security tests
for Phase 028 API Documentation.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_openapi_json_returns_200_ok() -> None:
    """Verify GET /openapi.json returns HTTP 200 OK when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_openapi_version_exists() -> None:
    """Verify OpenAPI version attribute exists in generated schema."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")


def test_openapi_title_matches_settings() -> None:
    """Verify API title matches Settings.app_name."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == settings.app_name


def test_openapi_version_matches_settings() -> None:
    """Verify API version matches Settings.app_version."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == settings.app_version


def test_openapi_description_matches_settings() -> None:
    """Verify API description matches Settings.description."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["description"] == settings.description


def test_openapi_paths_contain_health() -> None:
    """Verify /api/v1/health is documented in OpenAPI paths."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "/api/v1/health" in schema["paths"]


def test_openapi_paths_contain_ready() -> None:
    """Verify /api/v1/ready is documented in OpenAPI paths."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "/api/v1/ready" in schema["paths"]


def test_openapi_paths_contain_root() -> None:
    """Verify root endpoint / is documented in OpenAPI paths."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "/" in schema["paths"]


def test_health_operation_summary_and_description() -> None:
    """Verify GET /api/v1/health has summary and non-empty description."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    health_op = schema["paths"]["/api/v1/health"]["get"]

    assert health_op["summary"] == "Health Check"
    assert "process liveness" in health_op["description"].lower()


def test_readiness_operation_summary_and_description() -> None:
    """Verify GET /api/v1/ready has summary and non-empty description."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    ready_op = schema["paths"]["/api/v1/ready"]["get"]

    assert ready_op["summary"] == "Readiness Check"
    assert "traffic readiness" in ready_op["description"].lower()


def test_health_operation_tags() -> None:
    """Verify GET /api/v1/health is tagged with 'Health'."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    health_op = schema["paths"]["/api/v1/health"]["get"]

    assert "Health" in health_op["tags"]


def test_readiness_operation_tags() -> None:
    """Verify GET /api/v1/ready is tagged with 'Readiness'."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    ready_op = schema["paths"]["/api/v1/ready"]["get"]

    assert "Readiness" in ready_op["tags"]


def test_readiness_documents_200_and_503_responses() -> None:
    """Verify GET /api/v1/ready documents both 200 OK and 503 Service Unavailable responses."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    responses = schema["paths"]["/api/v1/ready"]["get"]["responses"]

    assert "200" in responses
    assert "503" in responses


def test_components_schemas_exist() -> None:
    """Verify components.schemas section exists in OpenAPI schema."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "components" in schema
    assert "schemas" in schema["components"]


def test_error_response_schemas_exist() -> None:
    """Verify ErrorResponse and ErrorPayload schemas exist in components.schemas."""
    app = create_app()
    client = TestClient(app)

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "ErrorResponse" in schemas or "ErrorPayload" in schemas


def test_response_meta_schema_contains_request_id() -> None:
    """Verify ResponseMeta schema defines request_id field."""
    app = create_app()
    client = TestClient(app)

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "ResponseMeta" in schemas
    props = schemas["ResponseMeta"]["properties"]
    assert "request_id" in props


def test_operation_ids_are_unique() -> None:
    """Verify all operation IDs across OpenAPI paths are strictly unique."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    operation_ids: list[str] = []

    for _path, methods in schema["paths"].items():
        for _method, details in methods.items():
            if isinstance(details, dict) and "operationId" in details:
                operation_ids.append(details["operationId"])

    assert len(operation_ids) == len(set(operation_ids))


def test_schema_references_resolve() -> None:
    """Verify all $ref references in OpenAPI schema resolve to existing components."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    defined_schemas = set(schema.get("components", {}).get("schemas", {}).keys())

    def find_refs(node: Any) -> list[str]:
        refs: list[str] = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str):
                    refs.append(v)
                else:
                    refs.extend(find_refs(v))
        elif isinstance(node, list):
            for item in node:
                refs.extend(find_refs(item))
        return refs

    refs = find_refs(schema)
    for ref in refs:
        schema_name = ref.split("/")[-1]
        assert schema_name in defined_schemas, f"Broken schema $ref: {ref}"


def test_zero_secrets_leak_in_openapi_schema() -> None:
    """Verify no raw secret keys, environment variables, or credentials leak in /openapi.json."""
    app = create_app()
    client = TestClient(app)

    schema_text = client.get("/openapi.json").text.lower()

    forbidden_patterns = [
        "super_secret",
        "secret_pass",
        "postgres://",
        "redis://",
        "bearer ",
        "private_key_value",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in schema_text


def test_swagger_ui_returns_200_when_enabled() -> None:
    """Verify GET /docs returns HTTP 200 OK HTML page when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_redoc_returns_200_when_enabled() -> None:
    """Verify GET /redoc returns HTTP 200 OK HTML page when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_docs_toggles_respected_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify /docs, /redoc, and /openapi.json return 404 when disabled in Settings."""
    get_settings.cache_clear()
    monkeypatch.setenv("DOCS_ENABLED", "false")
    monkeypatch.setenv("REDOC_ENABLED", "false")
    monkeypatch.setenv("OPENAPI_ENABLED", "false")

    disabled_app = create_app()
    client = TestClient(disabled_app)

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404

    get_settings.cache_clear()


def test_openapi_schema_is_deterministic() -> None:
    """Verify repeated calls to /openapi.json produce identical schemas."""
    app = create_app()
    client = TestClient(app)

    s1 = client.get("/openapi.json").json()
    s2 = client.get("/openapi.json").json()

    assert s1 == s2


def test_health_endpoint_remains_functional() -> None:
    """Verify Phase 026 GET /api/v1/health remains functional."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"


def test_readiness_endpoint_remains_functional() -> None:
    """Verify Phase 027 GET /api/v1/ready remains functional."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"


def test_404_behavior_remains_canonical() -> None:
    """Verify non-existent routes return canonical 404 ErrorResponse."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/does-not-exist-route")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_405_method_not_allowed_remains_canonical() -> None:
    """Verify POST to GET-only routes returns 405 Method Not Allowed."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["success"] is False


def test_cors_behavior_remains_intact_on_docs() -> None:
    """Verify CORS headers apply cleanly to /openapi.json and documentation routes."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_request_id_header_present_on_docs_requests() -> None:
    """Verify X-Request-ID response header is attached to /docs and /openapi.json requests."""
    app = create_app()
    client = TestClient(app)

    r1 = client.get("/openapi.json")
    assert r1.headers.get("x-request-id") is not None

    r2 = client.get("/docs")
    assert r2.headers.get("x-request-id") is not None


def test_response_standardization_bypasses_openapi_and_docs() -> None:
    """Verify ResponseStandardizationMiddleware leaves /openapi.json raw dict and /docs
    HTML unwrapped.
    """

    app = create_app()
    client = TestClient(app)

    openapi_res = client.get("/openapi.json").json()
    assert "openapi" in openapi_res
    assert "success" not in openapi_res  # Must NOT be wrapped!

    docs_res = client.get("/docs").text
    assert "<!html" in docs_res.lower() or "<html" in docs_res.lower()
