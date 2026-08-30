"""Centralized OpenAPI configuration, metadata, and custom schema generator for AGENTPAY."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import get_settings

OPENAPI_CONTACT: dict[str, str] = {
    "name": "AGENTPAY Platform Engineering",
}

OPENAPI_TAGS: list[dict[str, Any]] = [
    {
        "name": "System",
        "description": "Core system status, platform root, and operational endpoints.",
    },
    {
        "name": "Health",
        "description": "Process liveness probes for container lifecycle management.",
    },
    {
        "name": "Readiness",
        "description": "Traffic readiness probes for load balancing and service discovery.",
    },
]

OPENAPI_SERVERS: list[dict[str, str]] = [
    {
        "url": "http://localhost:8000",
        "description": "Local Development Server",
    },
]


def configure_openapi(app: FastAPI) -> None:
    """Configure centralized, cached, deterministic OpenAPI schema generator for FastAPI.

    Attaches metadata, contact information, tag descriptions, server list,
    vendor extensions, and cached schema generation to the application.
    """
    settings = get_settings()

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title or settings.app_name,
            version=app.version or settings.app_version,
            description=app.description or settings.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
            servers=OPENAPI_SERVERS,
            contact=OPENAPI_CONTACT,
        )

        # Attach vendor extension metadata
        openapi_schema["x-service"] = "agentpay-api"
        openapi_schema["x-api-version"] = settings.app_version

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
