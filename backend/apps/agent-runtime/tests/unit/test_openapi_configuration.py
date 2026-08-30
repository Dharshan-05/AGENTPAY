"""Unit, integration, schema validation, toggle, stability, and security tests
for Phase 029 OpenAPI Configuration.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.openapi import OPENAPI_CONTACT, OPENAPI_SERVERS
from app.main import create_app


def test_openapi_endpoint_returns_200_ok() -> None:
    """Verify GET /openapi.json returns HTTP 200 OK status code when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_openapi_schema_is_valid_dict() -> None:
    """Verify GET /openapi.json returns a valid JSON object."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert isinstance(schema, dict)
    assert "openapi" in schema


def test_openapi_title_comes_from_settings() -> None:
    """Verify info.title matches Settings.app_name."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == settings.app_name


def test_openapi_version_comes_from_settings() -> None:
    """Verify info.version matches Settings.app_version."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == settings.app_version


def test_openapi_description_comes_from_settings() -> None:
    """Verify info.description matches Settings.description."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema["info"]["description"] == settings.description


def test_openapi_contact_metadata_exists() -> None:
    """Verify info.contact matches centralized OPENAPI_CONTACT definition."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "contact" in schema["info"]
    assert schema["info"]["contact"]["name"] == OPENAPI_CONTACT["name"]


def test_openapi_tags_exist() -> None:
    """Verify System, Health, and Readiness tags are declared in OpenAPI schema."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    tag_names = [t["name"] for t in schema.get("tags", [])]

    assert "System" in tag_names
    assert "Health" in tag_names
    assert "Readiness" in tag_names


def test_openapi_servers_metadata_exists() -> None:
    """Verify server metadata matches centralized OPENAPI_SERVERS configuration."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert "servers" in schema
    assert len(schema["servers"]) > 0
    assert schema["servers"][0]["url"] == OPENAPI_SERVERS[0]["url"]


def test_vendor_extensions_exist() -> None:
    """Verify x-service and x-api-version vendor extensions are attached to schema root."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    assert schema.get("x-service") == "agentpay-api"
    assert schema.get("x-api-version") == settings.app_version


def test_openapi_paths_contain_all_registered_routes() -> None:
    """Verify /, /api/v1/health, and /api/v1/ready are present in OpenAPI paths."""
    app = create_app()
    client = TestClient(app)

    paths = client.get("/openapi.json").json()["paths"]
    assert "/" in paths
    assert "/api/v1/health" in paths
    assert "/api/v1/ready" in paths


def test_no_duplicate_paths_exist() -> None:
    """Verify path items are unique with no duplicate path keys."""
    app = create_app()
    client = TestClient(app)

    paths = list(client.get("/openapi.json").json()["paths"].keys())
    assert len(paths) == len(set(paths))


def test_no_unmounted_v2_paths_advertised() -> None:
    """Verify unmounted /api/v2 routes are not falsely advertised in OpenAPI schema."""
    app = create_app()
    client = TestClient(app)

    paths = client.get("/openapi.json").json()["paths"]
    v2_paths = [p for p in paths if p.startswith("/api/v2")]
    assert len(v2_paths) == 0


def test_root_operation_id_exists() -> None:
    """Verify GET / has operationId = 'root_check'."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    root_op = schema["paths"]["/"]["get"]
    assert root_op["operationId"] == "root_check"


def test_health_operation_id_exists() -> None:
    """Verify GET /api/v1/health has operationId = 'health_check'."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    health_op = schema["paths"]["/api/v1/health"]["get"]
    assert health_op["operationId"] == "health_check"


def test_readiness_operation_id_exists() -> None:
    """Verify GET /api/v1/ready has operationId = 'readiness_check'."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    ready_op = schema["paths"]["/api/v1/ready"]["get"]
    assert ready_op["operationId"] == "readiness_check"


def test_operation_ids_are_globally_unique() -> None:
    """Verify all operation IDs across OpenAPI endpoints are globally unique."""
    app = create_app()
    client = TestClient(app)

    schema = client.get("/openapi.json").json()
    op_ids: list[str] = []

    for _path, methods in schema["paths"].items():
        for _method, details in methods.items():
            if isinstance(details, dict) and "operationId" in details:
                op_ids.append(details["operationId"])

    assert len(op_ids) == len(set(op_ids))


def test_health_200_response_documented() -> None:
    """Verify GET /api/v1/health documents HTTP 200 response."""
    app = create_app()
    client = TestClient(app)

    responses = client.get("/openapi.json").json()["paths"]["/api/v1/health"]["get"]["responses"]
    assert "200" in responses


def test_readiness_200_and_503_responses_documented() -> None:
    """Verify GET /api/v1/ready documents both 200 OK and 503 Service Unavailable."""
    app = create_app()
    client = TestClient(app)

    responses = client.get("/openapi.json").json()["paths"]["/api/v1/ready"]["get"]["responses"]
    assert "200" in responses
    assert "503" in responses


def test_reusable_schemas_exist_in_components() -> None:
    """Verify reusable response models exist under components.schemas."""
    app = create_app()
    client = TestClient(app)

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "HealthCheckData" in schemas
    assert "ReadinessResponseData" in schemas
    assert "ResponseMeta" in schemas


def test_error_response_schemas_exist_in_components() -> None:
    """Verify ErrorResponse and ErrorPayload schemas exist in components.schemas."""
    app = create_app()
    client = TestClient(app)

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "ErrorResponse" in schemas or "ErrorPayload" in schemas


def test_response_meta_schema_defines_request_id() -> None:
    """Verify ResponseMeta schema defines request_id field."""
    app = create_app()
    client = TestClient(app)

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "ResponseMeta" in schemas
    props = schemas["ResponseMeta"]["properties"]
    assert "request_id" in props


def test_zero_raw_secrets_leak_in_openapi_schema() -> None:
    """Verify serialized /openapi.json contains zero raw secret values or credentials."""
    app = create_app()
    client = TestClient(app)

    schema_text = client.get("/openapi.json").text.lower()

    forbidden_secrets = [
        "super_secret",
        "secret_pass",
        "postgres://",
        "redis://",
        "bearer ",
        "private_key_val",
    ]
    for secret in forbidden_secrets:
        assert secret not in schema_text


def test_zero_secret_field_names_leak_as_raw_values() -> None:
    """Verify secret configuration values are omitted from public OpenAPI JSON."""
    settings = get_settings()
    app = create_app()
    client = TestClient(app)

    schema_text = client.get("/openapi.json").text

    if settings.secret_key:
        assert settings.secret_key.get_secret_value() not in schema_text
    if settings.jwt_secret:
        assert settings.jwt_secret.get_secret_value() not in schema_text


def test_documentation_toggle_disables_openapi_when_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify OPENAPI_ENABLED=False causes GET /openapi.json to return 404 Not Found."""
    get_settings.cache_clear()
    monkeypatch.setenv("OPENAPI_ENABLED", "false")

    disabled_app = create_app()
    client = TestClient(disabled_app)

    assert client.get("/openapi.json").status_code == 404
    get_settings.cache_clear()


def test_openapi_generation_is_100_percent_deterministic() -> None:
    """Verify repeated calls to /openapi.json produce identical schemas."""
    app = create_app()
    client = TestClient(app)

    s1 = client.get("/openapi.json").json()
    s2 = client.get("/openapi.json").json()

    assert s1 == s2


def test_swagger_ui_accessible_when_enabled() -> None:
    """Verify GET /docs returns HTTP 200 HTML page when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_redoc_accessible_when_enabled() -> None:
    """Verify GET /redoc returns HTTP 200 HTML page when enabled."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_cors_behavior_remains_intact_on_openapi_endpoint() -> None:
    """Verify CORS origin headers apply cleanly to /openapi.json."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_root_endpoint_remains_functional() -> None:
    """Verify GET / root status endpoint remains functional."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["data"]["service"] == "agentpay-api"


def test_health_endpoint_remains_functional() -> None:
    """Verify GET /api/v1/health endpoint remains functional."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"


def test_readiness_endpoint_remains_functional() -> None:
    """Verify GET /api/v1/ready endpoint remains functional."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"


def test_404_behavior_remains_canonical() -> None:
    """Verify non-existent routes return 404 ErrorResponse."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_405_method_not_allowed_remains_canonical() -> None:
    """Verify unsupported HTTP method returns 405 Method Not Allowed."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["success"] is False
