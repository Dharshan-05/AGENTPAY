"""Security Policy Management REST Controller Router for AGENTPAY (Phases 185–186)."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.policy_service import PolicyService
from app.domain.authorization.permissions_registry import (
    POLICIES_ACTIVATE,
    POLICIES_ARCHIVE,
    POLICIES_CREATE,
    POLICIES_DEACTIVATE,
    POLICIES_READ,
    POLICIES_UPDATE,
)
from app.domain.exceptions.policy_exceptions import (
    PolicyAlreadyExistsError,
    PolicyNotFoundError,
    PolicyValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.policies import (
    PolicyCreateRequest,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdateRequest,
)

logger = logging.getLogger("agentguard.api.policies")

policies_router = APIRouter(prefix="/policies", tags=["Security & Risk - Policies"])


def get_policy_service() -> PolicyService:
    """Dependency factory for PolicyService."""
    return PolicyService()


@policies_router.post(
    "",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Security Policy",
    description="Create a new Security Policy within tenant scope (Phase 186).",
    operation_id="create_policy",
    dependencies=[Depends(require_permission(POLICIES_CREATE))],
)
async def create_policy(
    request: PolicyCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Create a security policy."""
    try:
        return await service.create_policy(
            db, tenant_id=current_user.tenant_id, request=request, user_id=current_user.user.id
        )
    except PolicyAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PolicyValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@policies_router.get(
    "",
    response_model=PolicyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Security Policies",
    description="List policies in tenant scope with optional filtering and pagination (Phase 186).",
    operation_id="list_policies",
    dependencies=[Depends(require_permission(POLICIES_READ))],
)
async def list_policies(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
    status_filter: str | None = Query(default=None, alias="status"),
    policy_type_filter: str | None = Query(default=None, alias="policy_type"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> PolicyListResponse:
    """List security policies."""
    return await service.list_policies(
        db,
        tenant_id=current_user.tenant_id,
        status_filter=status_filter,
        policy_type_filter=policy_type_filter,
        page=page,
        size=size,
    )


@policies_router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Security Policy",
    description="Lookup a security policy by policy_id within tenant boundary (Phase 186).",
    operation_id="get_policy",
    dependencies=[Depends(require_permission(POLICIES_READ))],
)
async def get_policy(
    policy_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Get security policy details."""
    try:
        return await service.get_policy(db, tenant_id=current_user.tenant_id, policy_id=policy_id)
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@policies_router.patch(
    "/{policy_id}",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Security Policy",
    description="Update mutable attributes of a security policy, incrementing version (Phase 186).",  # noqa: E501
    operation_id="update_policy",
    dependencies=[Depends(require_permission(POLICIES_UPDATE))],
)
async def update_policy(
    policy_id: uuid.UUID,
    request: PolicyUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Update security policy attributes."""
    try:
        return await service.update_policy(
            db, tenant_id=current_user.tenant_id, policy_id=policy_id, request=request
        )
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PolicyValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@policies_router.post(
    "/{policy_id}/activate",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Security Policy",
    description="Set policy status to active (Phase 186).",
    operation_id="activate_policy",
    dependencies=[Depends(require_permission(POLICIES_ACTIVATE))],
)
async def activate_policy(
    policy_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Activate security policy."""
    try:
        return await service.activate_policy(
            db, tenant_id=current_user.tenant_id, policy_id=policy_id
        )
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@policies_router.post(
    "/{policy_id}/deactivate",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate Security Policy",
    description="Set policy status to inactive (Phase 186).",
    operation_id="deactivate_policy",
    dependencies=[Depends(require_permission(POLICIES_DEACTIVATE))],
)
async def deactivate_policy(
    policy_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Deactivate security policy."""
    try:
        return await service.deactivate_policy(
            db, tenant_id=current_user.tenant_id, policy_id=policy_id
        )
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@policies_router.post(
    "/{policy_id}/archive",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive Security Policy",
    description="Soft-delete/archive security policy (Phase 186).",
    operation_id="archive_policy",
    dependencies=[Depends(require_permission(POLICIES_ARCHIVE))],
)
async def archive_policy(
    policy_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> PolicyResponse:
    """Archive security policy."""
    try:
        return await service.archive_policy(
            db, tenant_id=current_user.tenant_id, policy_id=policy_id
        )
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
