"""Centralized service bootstrap coordinator for AGENTPAY backend service."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.lifespan import lifespan, register_lifecycle_component
from app.core.logging import configure_logging
from app.core.openapi import configure_openapi
from app.exceptions.handler import register_exception_handlers
from app.infrastructure.database import DatabaseLifecycleComponent
from app.middleware.registration import register_middleware


def bootstrap_app(settings: Settings | None = None) -> FastAPI:
    """Bootstrap and orchestrate the AGENTPAY FastAPI backend service foundation.

    Coordinates configuration loading, structured logging setup, FastAPI
    application instantiation, OpenAPI metadata setup, middleware registration,
    exception handler registration, lifespan lifecycle registration, and API router mounting.
    """
    current_settings = settings if settings is not None else get_settings()

    # 1. Configure centralized logging infrastructure
    configure_logging(current_settings)

    # 2. Register database lifecycle component
    register_lifecycle_component(DatabaseLifecycleComponent())

    # 2. Instantiate FastAPI application framework
    application = FastAPI(
        title=current_settings.app_name,
        description=current_settings.description,
        version=current_settings.app_version,
        docs_url=current_settings.docs_url,
        redoc_url=current_settings.redoc_url,
        openapi_url=current_settings.openapi_url,
        lifespan=lifespan,
    )

    # 3. Configure centralized OpenAPI documentation metadata and schema engine
    configure_openapi(application)

    # 4. Register middleware foundation pipeline
    register_middleware(application)

    # 5. Register exception handler translation pipeline
    register_exception_handlers(application)

    # 6. Mount root and versioned API routers
    application.include_router(api_router)

    return application
