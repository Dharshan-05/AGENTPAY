"""Purchase Planning REST controller router for AGENTPAY (Phase 180)."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.purchase_planning_service import PurchasePlanningService
from app.domain.authorization.permissions_registry import PRODUCTS_READ
from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.purchase_planning import (
    PurchasePlanCreateRequest,
    PurchasePlanResponse,
)

logger = logging.getLogger("agentpay.api.purchase_plans")

purchase_plans_router = APIRouter(
    prefix="/purchase-plans", tags=["Commerce Engine - Purchase Planning"]
)


def get_purchase_planning_service() -> PurchasePlanningService:
    """Dependency factory for PurchasePlanningService."""
    return PurchasePlanningService()


@purchase_plans_router.post(
    "",
    response_model=PurchasePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Plan",
    description="Validate items, inventory, offers, and create a purchase plan snapshot (Phase 180).",  # noqa: E501
    operation_id="create_purchase_plan",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def create_purchase_plan(
    request: PurchasePlanCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PurchasePlanningService, Depends(get_purchase_planning_service)],
) -> PurchasePlanResponse:
    """Create a validated, idempotent purchase plan."""
    try:
        return await service.create_purchase_plan(
            db, tenant_id=current_user.tenant_id, request=request
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@purchase_plans_router.get(
    "/{plan_id}",
    response_model=PurchasePlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Purchase Plan",
    description="Lookup a purchase plan by plan_id within tenant scope (Phase 180).",
    operation_id="get_purchase_plan",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_purchase_plan(
    plan_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PurchasePlanningService, Depends(get_purchase_planning_service)],
) -> PurchasePlanResponse:
    """Lookup purchase plan details."""
    try:
        return await service.get_purchase_plan(
            db, tenant_id=current_user.tenant_id, plan_id=plan_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
