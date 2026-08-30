"""Merchant Management REST controller router for AGENTPAY (Phase 165)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.merchant_service import MerchantService
from app.domain.authorization.permissions_registry import (
    MERCHANTS_ARCHIVE,
    MERCHANTS_CREATE,
    MERCHANTS_READ,
    MERCHANTS_SUSPEND,
    MERCHANTS_UPDATE,
)
from app.domain.exceptions.agent_exceptions import (
    MerchantAlreadyExistsError,
    MerchantNotFoundError,
    MerchantValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.merchants import (
    MerchantCreateRequest,
    MerchantListResponse,
    MerchantResponse,
    MerchantUpdateRequest,
)

logger = logging.getLogger("agentpay.api.merchants")

merchants_router = APIRouter(prefix="/merchants", tags=["Commerce Engine - Merchants"])


def get_merchant_service() -> MerchantService:
    """Dependency factory for MerchantService."""
    return MerchantService()


@merchants_router.post(
    "",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Merchant",
    description="Register a new commercial Merchant entity in AGENTPAY (Phase 165).",
    operation_id="create_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_CREATE))],
)
async def create_merchant(
    request: MerchantCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Create a new merchant."""
    try:
        return await service.create_merchant(db, tenant_id=current_user.tenant_id, request=request)
    except MerchantAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except MerchantValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@merchants_router.get(
    "",
    response_model=MerchantListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Merchants",
    description="List tenant-scoped merchants using keyset pagination (Phase 165).",
    operation_id="list_merchants",
    dependencies=[Depends(require_permission(MERCHANTS_READ))],
)
async def list_merchants(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
    status_filter: Annotated[
        str | None, Query(alias="status", description="Optional filter by merchant status")
    ] = None,
    cursor_created_at: Annotated[
        datetime | None, Query(description="Keyset cursor datetime")
    ] = None,
    cursor_id: Annotated[uuid.UUID | None, Query(description="Keyset cursor UUID")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Page limit")] = 20,
) -> MerchantListResponse:
    """List merchants for tenant."""
    return await service.list_merchants(
        db,
        tenant_id=current_user.tenant_id,
        status=status_filter,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        limit=limit,
    )


@merchants_router.get(
    "/{merchant_id}",
    response_model=MerchantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Merchant Detail",
    description="Lookup a merchant by merchant_id within tenant scope (Phase 165).",
    operation_id="get_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_READ))],
)
async def get_merchant(
    merchant_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Lookup merchant detail."""
    try:
        return await service.get_merchant(
            db, tenant_id=current_user.tenant_id, merchant_id=merchant_id
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@merchants_router.patch(
    "/{merchant_id}",
    response_model=MerchantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Merchant",
    description="Update merchant details (Phase 165).",
    operation_id="update_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_UPDATE))],
)
async def update_merchant(
    merchant_id: uuid.UUID,
    request: MerchantUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Update merchant details."""
    try:
        return await service.update_merchant(
            db, tenant_id=current_user.tenant_id, merchant_id=merchant_id, request=request
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MerchantValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@merchants_router.post(
    "/{merchant_id}/activate",
    response_model=MerchantResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Merchant",
    description="Activate a merchant (Phase 165).",
    operation_id="activate_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_UPDATE))],
)
async def activate_merchant(
    merchant_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Activate a merchant."""
    try:
        return await service.activate_merchant(
            db, tenant_id=current_user.tenant_id, merchant_id=merchant_id
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@merchants_router.post(
    "/{merchant_id}/suspend",
    response_model=MerchantResponse,
    status_code=status.HTTP_200_OK,
    summary="Suspend Merchant",
    description="Suspend a merchant (Phase 165).",
    operation_id="suspend_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_SUSPEND))],
)
async def suspend_merchant(
    merchant_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Suspend a merchant."""
    try:
        return await service.suspend_merchant(
            db, tenant_id=current_user.tenant_id, merchant_id=merchant_id
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@merchants_router.post(
    "/{merchant_id}/archive",
    response_model=MerchantResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive Merchant",
    description="Archive (soft delete) a merchant (Phase 165).",
    operation_id="archive_merchant",
    dependencies=[Depends(require_permission(MERCHANTS_ARCHIVE))],
)
async def archive_merchant(
    merchant_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[MerchantService, Depends(get_merchant_service)],
) -> MerchantResponse:
    """Archive a merchant."""
    try:
        return await service.archive_merchant(
            db, tenant_id=current_user.tenant_id, merchant_id=merchant_id
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
