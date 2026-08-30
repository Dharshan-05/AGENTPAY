"""AGENTPAY Permission Management API Controller (Phase 113).

Endpoints:
    GET /api/v1/permissions          — List all registered permissions
    GET /api/v1/permissions/{id}     — Get permission by ID

Authorization:
    Requires permissions:read.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser
from app.api.dependencies.authorization import require_permission
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.permissions_registry import PERMISSIONS_READ
from app.infrastructure.database.session import get_db_session
from app.schemas.permissions import PermissionResponse

permissions_router = APIRouter(tags=["Permission Management"])
_authz_service = AuthorizationService()


def get_authz_service() -> AuthorizationService:
    """Dependency provider for AuthorizationService."""
    return _authz_service


@permissions_router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    summary="List Permissions",
    description="List all registered system permissions.",
    operation_id="list_permissions",
)
async def list_permissions(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(PERMISSIONS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> list[PermissionResponse]:
    """List all registered permissions."""
    perms = await service.list_permissions(db)
    return [PermissionResponse.model_validate(p) for p in perms]


@permissions_router.get(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Get Permission",
    description="Retrieve a specific permission by ID.",
    operation_id="get_permission",
)
async def get_permission(
    permission_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(PERMISSIONS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> PermissionResponse:
    """Retrieve a permission by ID."""
    perm = await service.get_permission(db, permission_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found.")
    return PermissionResponse.model_validate(perm)
