"""Unit, integration, and security tests for Phase 023 Request Validation."""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

import pytest
from fastapi import Path, Query
from fastapi.testclient import TestClient
from pydantic import Field, SecretStr

from app.core.logging import configure_logging
from app.main import create_app
from app.schemas.requests import StrictRequestModel


class SampleMode(StrEnum):
    """Test enum mode."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class NestedConfig(StrictRequestModel):
    """Test nested schema."""

    mode: SampleMode
    timeout: int = Field(..., ge=1, le=60)


class SampleRequest(StrictRequestModel):
    """Test request model with strict validation boundaries."""

    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=18, le=120)
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    is_admin: bool = Field(...)

    config: NestedConfig
    tags: list[str] = Field(..., min_length=1, max_length=5)
    password: SecretStr | None = None
    api_key: str | None = None


def test_valid_request_payload() -> None:
    """Verify valid request payload passes validation successfully."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok", "name": req.name}

    client = TestClient(test_app)
    payload = {
        "name": "Alice",
        "age": 30,
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent", "pay"],
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == {"status": "ok", "name": "Alice"}


def test_missing_required_field() -> None:
    """Verify payload missing required field returns 400 Bad Request VALIDATION_ERROR."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    payload = {
        "age": 30,
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent"],
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed."
    assert any(err["location"] == "body.name" for err in data["error"]["details"])


def test_wrong_field_type() -> None:
    """Verify payload with invalid field type returns 400 VALIDATION_ERROR."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    payload = {
        "name": "Alice",
        "age": "not-an-integer",
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent"],
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_extra_field_rejection() -> None:
    """Verify extra unexpected field is rejected when strict mode extra='forbid' is used."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    payload = {
        "name": "Alice",
        "age": 30,
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent"],
        "unexpected_field": "malicious_input",
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert any("unexpected_field" in err["location"] for err in data["error"]["details"])


def test_string_length_constraints() -> None:
    """Verify string exceeding max_length or under min_length is rejected."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    payload = {
        "name": "A",  # Less than min_length=2
        "age": 30,
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent"],
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_numeric_query_parameter_bounds() -> None:
    """Verify query parameter bounds (page >= 1, page_size <= 100) are enforced."""
    test_app = create_app()

    @test_app.get("/test-query")
    def query_route(
        page: Annotated[int, Query(ge=1)],
        page_size: Annotated[int, Query(ge=1, le=100)],
    ) -> dict[str, int]:
        return {"page": page, "page_size": page_size}

    client = TestClient(test_app)
    response = client.get("/test-query?page=0&page_size=500")
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    locations = [err["location"] for err in data["error"]["details"]]
    assert "query.page" in locations
    assert "query.page_size" in locations


def test_uuid_path_parameter_validation() -> None:
    """Verify path parameter UUID format is strictly enforced."""
    test_app = create_app()

    @test_app.get("/test-path/{resource_id}")
    def path_route(resource_id: Annotated[UUID, Path()]) -> dict[str, str]:
        return {"resource_id": str(resource_id)}

    client = TestClient(test_app)
    response = client.get("/test-path/not-a-valid-uuid")
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert any(err["location"] == "path.resource_id" for err in data["error"]["details"])


def test_nested_extra_field_rejection() -> None:
    """Verify unexpected extra field in nested object is rejected."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    payload = {
        "name": "Alice",
        "age": 30,
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30, "extra_nested": "bad"},
        "tags": ["agent"],
    }
    response = client.post("/test-validate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_malformed_json_syntax_error() -> None:
    """Verify malformed JSON syntax produces 400 VALIDATION_ERROR with zero traceback."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    response = client.post(
        "/test-validate",
        content="{invalid_json_syntax",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Invalid JSON payload syntax."
    assert data["error"]["details"] is None


def test_secret_protection_in_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    """Verify secret values in body/query/headers are NEVER echoed in error details or logs."""
    configure_logging()
    test_app = create_app()

    @test_app.post("/test-secret-validate")
    def secret_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    secret_body_val = "SUPER_SECRET_BODY_PASSWORD_99"
    secret_key_val = "SUPER_SECRET_API_KEY_77"
    payload = {
        "name": "Alice",
        "age": "invalid-age",
        "amount": "100.50",
        "is_admin": True,
        "config": {"mode": "active", "timeout": 30},
        "tags": ["agent"],
        "password": secret_body_val,
        "api_key": secret_key_val,
    }
    response = client.post(
        "/test-secret-validate",
        json=payload,
        headers={"Authorization": "Bearer SUPER_SECRET_TOKEN_55"},
    )
    assert response.status_code == 400

    response_text = response.text
    assert secret_body_val not in response_text
    assert secret_key_val not in response_text
    assert "SUPER_SECRET_TOKEN_55" not in response_text

    for record in caplog.records:
        log_msg = record.getMessage()
        assert secret_body_val not in log_msg
        assert secret_key_val not in log_msg
        assert "SUPER_SECRET_TOKEN_55" not in log_msg


def test_cors_preservation_on_validation_error() -> None:
    """Verify CORS headers are returned on 400 validation error responses."""
    test_app = create_app()

    @test_app.post("/test-validate")
    def validate_route(req: SampleRequest) -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    response = client.post(
        "/test-validate",
        json={"invalid": "payload"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
