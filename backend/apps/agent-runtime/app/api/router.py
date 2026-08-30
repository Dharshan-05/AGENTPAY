"""Root API router registration and root endpoint."""

from typing import Any

from fastapi import APIRouter

from app.api.v1.router import api_v1_router
from app.core.config import get_settings

api_router = APIRouter()

# Include versioned routers under /api/v1 prefix from Settings
api_router.include_router(api_v1_router, prefix=get_settings().api_v1_str)


@api_router.get(
    "/",
    operation_id="root_check",
    summary="Root Status Check",
    description="Service status endpoint returning operational state.",
    tags=["System"],
)
async def root_endpoint() -> dict[str, Any]:
    """Root status endpoint."""
    return {
        "service": "agentpay-api",
        "status": "running",
    }
