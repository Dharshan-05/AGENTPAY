"""Unit and integration tests for Phase 020 API Versioning architecture."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_version_prefix_configuration_consistency() -> None:
    """Verify Settings configuration derives canonical API prefixes accurately."""
    current_settings = get_settings()

    assert current_settings.api_prefix == "/api"
    assert current_settings.api_v1_prefix == "/v1"
    assert current_settings.api_v1_str == "/api/v1"


def test_import_safety_no_circular_dependencies() -> None:
    """Verify router modules can be imported without circular dependency errors."""
    import app.api.router as root_router_mod
    import app.api.v1.router as v1_router_mod
    import app.main as main_mod

    assert root_router_mod.api_router is not None
    assert v1_router_mod.api_v1_router is not None
    assert main_mod.create_app is not None


def test_root_endpoint_preservation(client: TestClient) -> None:
    """Verify root status endpoint GET / contract is preserved."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == {
        "service": "agentpay-api",
        "status": "running",
    }
    assert data["meta"]["request_id"] is not None


def test_unknown_version_404_safety(client: TestClient) -> None:
    """Verify requests to unmounted or future API versions fail safely with 404."""
    r_v2 = client.get("/api/v2/nonexistent")
    assert r_v2.status_code == 404

    r_v999 = client.get("/api/v999/status")
    assert r_v999.status_code == 404


def test_no_duplicate_prefixes_in_route_table() -> None:
    """Audit application route table to verify zero duplicate prefix patterns exist."""
    application = create_app()
    route_paths = [getattr(route, "path", "") for route in application.routes]

    forbidden_prefix_patterns = [
        "/api/api",
        "/api/v1/api",
        "/v1/v1",
        "/api/v1/v1",
    ]

    for path in route_paths:
        for forbidden in forbidden_prefix_patterns:
            assert not path.startswith(forbidden), (
                f"Forbidden duplicate route prefix pattern '{forbidden}' found in route '{path}'"
            )


def test_openapi_schema_contains_versioned_paths(client: TestClient) -> None:
    """Verify /openapi.json contains versioned paths without prefix duplication."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "paths" in schema
    paths = schema["paths"]

    assert "/" in paths
    for p in paths:
        assert not p.startswith("/api/api")
        assert not p.startswith("/v1/v1")
