"""AGENTPAY Role Management API Controller (Phase 112).

Endpoints:
    GET    /api/v1/roles                        — List tenant roles
    GET    /api/v1/roles/{role_id}              — Get role
    POST   /api/v1/roles                        — Create role
    PATCH  /api/v1/roles/{role_id}              — Update role
    GET    /api/v1/users/{user_id}/roles        — List user roles
    POST   /api/v1/users/{user_id}/roles        — Assign role to user
    DELETE /api/v1/users/{user_id}/roles/{role_id} — Remove role from user
    GET    /api/v1/roles/{role_id}/permissions  — List role permissions
    POST   /api/v1/roles/{role_id}/permissions  — Assign permission to role
    DELETE /api/v1/roles/{role_id}/permissions/{permission_id} — Revoke permission from role

Authorization:
    All endpoints require authentication via get_current_user.
    Role administration requires roles:read / roles:create / roles:update / roles:assign.
    Permission assignment requires permissions:assign.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser
from app.api.dependencies.authorization import require_permission
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.permissions_registry import (
    PERMISSIONS_ASSIGN,
    PERMISSIONS_REVOKE,
    ROLES_ASSIGN,
    ROLES_CREATE,
    ROLES_READ,
    ROLES_REVOKE,
    ROLES_UPDATE,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.permissions import (
    PermissionResponse,
    RolePermissionAssignRequest,
    RolePermissionResponse,
)
from app.schemas.roles import (
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleAssignRequest,
    UserRoleResponse,
)

roles_router = APIRouter(tags=["Role Management"])
_authz_service = AuthorizationService()


def get_authz_service() -> AuthorizationService:
    """Dependency provider for AuthorizationService."""
    return _authz_service


# ---------------------------------------------------------------------------
# Role CRUD
# ---------------------------------------------------------------------------


@roles_router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List Roles",
    description="List all active roles within the authenticated user's tenant scope.",
    operation_id="list_roles",
)
async def list_roles(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> list[RoleResponse]:
    """List all tenant-scoped roles."""
    roles = await service.list_roles(db, current_user.tenant_id)
    return [RoleResponse.model_validate(r) for r in roles]


@roles_router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Get Role",
    description="Retrieve a specific role within the authenticated user's tenant scope.",
    operation_id="get_role",
)
async def get_role(
    role_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> RoleResponse:
    """Retrieve a single role by ID within tenant scope."""
    role = await service.get_role(db, current_user.tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")
    return RoleResponse.model_validate(role)


@roles_router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Role",
    description="Create a new role within the authenticated user's tenant scope.",
    operation_id="create_role",
)
async def create_role(
    body: RoleCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_CREATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> RoleResponse:
    """Create a new tenant-scoped role. tenant_id in body must match authenticated tenant."""
    if body.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create roles in a different tenant.",
        )
    try:
        role = await service.create_role(db, current_user.tenant_id, body.name, body.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RoleResponse.model_validate(role)


@roles_router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update Role",
    description="Update an existing role within the authenticated user's tenant scope.",
    operation_id="update_role",
)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> RoleResponse:
    """Update a tenant-scoped role."""
    try:
        role = await service.update_role(
            db, current_user.tenant_id, role_id, body.model_dump(exclude_none=True)
        )
    except ValueError as exc:
        detail = str(exc)
        code = status.HTTP_409_CONFLICT if "already exists" in detail else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=detail) from exc
    return RoleResponse.model_validate(role)


# ---------------------------------------------------------------------------
# User-Role Assignment
# ---------------------------------------------------------------------------


@roles_router.get(
    "/users/{user_id}/roles",
    response_model=list[RoleResponse],
    summary="List User Roles",
    description="List all roles assigned to a user within the authenticated tenant scope.",
    operation_id="list_user_roles",
)
async def list_user_roles(
    user_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> list[RoleResponse]:
    """List roles assigned to a specific user within authenticated tenant."""
    roles = await service.list_user_roles(db, current_user.tenant_id, user_id)
    return [RoleResponse.model_validate(r) for r in roles]


@roles_router.post(
    "/users/{user_id}/roles",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Role to User",
    description="Assign a tenant-scoped role to a user. Both must belong to the same tenant.",
    operation_id="assign_role_to_user",
)
async def assign_role_to_user(
    user_id: uuid.UUID,
    body: UserRoleAssignRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_ASSIGN))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> UserRoleResponse:
    """Assign a role to a user within the authenticated tenant scope."""
    try:
        user_role = await service.assign_role_to_user(
            db, current_user.tenant_id, user_id, body.role_id
        )
    except ValueError as exc:
        detail = str(exc)
        code = (
            status.HTTP_409_CONFLICT if "already assigned" in detail else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=detail) from exc
    return UserRoleResponse.model_validate(user_role)


@roles_router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Remove Role from User",
    description="Remove a role assignment from a user within the authenticated tenant scope.",
    operation_id="remove_role_from_user",
)
async def remove_role_from_user(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(ROLES_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> None:
    """Remove role assignment from user within authenticated tenant scope."""
    try:
        await service.remove_role_from_user(db, current_user.tenant_id, user_id, role_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Role-Permission Management
# ---------------------------------------------------------------------------


@roles_router.get(
    "/roles/{role_id}/permissions",
    response_model=list[PermissionResponse],
    summary="List Role Permissions",
    description="List all permissions assigned to a specific role within tenant scope.",
    operation_id="list_role_permissions",
)
async def list_role_permissions(
    role_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(PERMISSIONS_ASSIGN))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> list[PermissionResponse]:
    """List permissions assigned to a role within authenticated tenant scope."""
    perms = await service.list_role_permissions(db, current_user.tenant_id, role_id)
    return [PermissionResponse.model_validate(p) for p in perms]


@roles_router.post(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Permission to Role",
    description="Assign a registered permission to a role within the authenticated tenant scope.",
    operation_id="assign_permission_to_role",
)
async def assign_permission_to_role(
    role_id: uuid.UUID,
    body: RolePermissionAssignRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(PERMISSIONS_ASSIGN))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> RolePermissionResponse:
    """Assign a permission to a role within the authenticated tenant scope."""
    try:
        rp = await service.grant_role_permission(
            db, current_user.tenant_id, role_id, body.permission_id
        )
    except ValueError as exc:
        detail = str(exc)
        code = (
            status.HTTP_409_CONFLICT if "already assigned" in detail else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=detail) from exc
    return RolePermissionResponse.model_validate(rp)


@roles_router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Revoke Permission from Role",
    description="Remove a permission assignment from a role within the authenticated tenant scope.",
    operation_id="revoke_permission_from_role",
)
async def revoke_permission_from_role(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(PERMISSIONS_REVOKE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthorizationService, Depends(get_authz_service)],
) -> None:
    """Revoke a permission from a role within the authenticated tenant scope."""
    try:
        await service.revoke_role_permission(db, current_user.tenant_id, role_id, permission_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
