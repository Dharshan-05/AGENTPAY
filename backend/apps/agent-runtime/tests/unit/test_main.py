"""Tests for FastAPI foundation, application factory, and endpoints."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.main import app as main_app
from app.main import create_app


def test_app_import_and_factory() -> None:
    """Verify application imports successfully and factory returns FastAPI instance."""
    assert isinstance(main_app, FastAPI)

    new_app = create_app()
    assert isinstance(new_app, FastAPI)
    assert new_app.title == settings.title
    assert new_app.version == settings.version


def test_root_endpoint_sync(client: TestClient) -> None:
    """Verify synchronous root endpoint returns expected service status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["service"] == "agentpay-api"
    assert data["data"]["status"] == "running"
    assert data["meta"]["request_id"] is not None


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client: AsyncClient) -> None:
    """Verify asynchronous root endpoint returns expected service status."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["service"] == "agentpay-api"
    assert data["data"]["status"] == "running"
    assert data["meta"]["request_id"] is not None


def test_openapi_schema(client: TestClient) -> None:
    """Verify OpenAPI JSON schema endpoint is accessible and contains expected metadata."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == settings.title
    assert schema["info"]["version"] == settings.version


def test_swagger_docs_endpoint(client: TestClient) -> None:
    """Verify Swagger UI docs endpoint returns HTTP 200."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint(client: TestClient) -> None:
    """Verify ReDoc documentation endpoint returns HTTP 200."""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_lifespan_execution() -> None:
    """Verify application startup and shutdown lifecycle execute cleanly without errors."""
    app_instance = create_app()
    with TestClient(app_instance) as test_client:
        res = test_client.get("/")
        assert res.status_code == 200
