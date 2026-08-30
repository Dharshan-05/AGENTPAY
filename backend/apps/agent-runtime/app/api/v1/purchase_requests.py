"""Purchase Request Pre-Execution & Transaction Orchestration REST controller router for AGENTPAY (Phase 181, 182 & 184)."""  # noqa: E501

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.commerce_transaction_orchestrator_service import (
    CommerceTransactionOrchestratorService,
)
from app.application.services.commerce_validation_service import CommerceValidationService
from app.application.services.purchase_request_service import PurchaseRequestService
from app.domain.authorization.permissions_registry import PRODUCTS_READ, PRODUCTS_UPDATE
from app.domain.exceptions.agent_exceptions import (
    ExecutionValidationError,
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.commerce_transaction_orchestration import (
    CommerceExecutionRequest,
    CommerceExecutionResponse,
)
from app.schemas.commerce_validation import CommerceValidationResult
from app.schemas.purchase_request import (
    PurchaseRequestCreateRequest,
    PurchaseRequestResponse,
)

logger = logging.getLogger("agentpay.api.purchase_requests")

purchase_requests_router = APIRouter(
    prefix="/purchase-requests", tags=["Commerce Engine - Purchase Requests"]
)


def get_purchase_request_service() -> PurchaseRequestService:
    """Dependency factory for PurchaseRequestService."""
    return PurchaseRequestService()


def get_commerce_validation_service() -> CommerceValidationService:
    """Dependency factory for CommerceValidationService."""
    return CommerceValidationService()


def get_commerce_orchestrator_service() -> CommerceTransactionOrchestratorService:
    """Dependency factory for CommerceTransactionOrchestratorService."""
    return CommerceTransactionOrchestratorService()


@purchase_requests_router.post(
    "",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Request",
    description="Validate plan, revalidate stale pricing/stock, check approval requirements, and create a pre-execution request (Phase 181).",  # noqa: E501
    operation_id="create_purchase_request",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def create_purchase_request(
    request: PurchaseRequestCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PurchaseRequestService, Depends(get_purchase_request_service)],
) -> PurchaseRequestResponse:
    """Create a validated pre-execution purchase request."""
    try:
        return await service.create_purchase_request(
            db, tenant_id=current_user.tenant_id, request=request
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@purchase_requests_router.get(
    "/{request_id}",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Purchase Request",
    description="Lookup a purchase request by request_id within tenant scope (Phase 181).",
    operation_id="get_purchase_request",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_purchase_request(
    request_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[PurchaseRequestService, Depends(get_purchase_request_service)],
) -> PurchaseRequestResponse:
    """Lookup purchase request details."""
    try:
        return await service.get_purchase_request(
            db, tenant_id=current_user.tenant_id, request_id=request_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@purchase_requests_router.post(
    "/{request_id}/validate",
    response_model=CommerceValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Authoritatively Validate Purchase Request",
    description="Authoritatively validate purchase request context, revalidating product status, stock, offers, and stale pricing (Phase 182).",  # noqa: E501
    operation_id="validate_purchase_request",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def validate_purchase_request(
    request_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    validation_service: Annotated[
        CommerceValidationService, Depends(get_commerce_validation_service)
    ],
) -> CommerceValidationResult:
    """Validate purchase request context."""
    try:
        return await validation_service.validate_commerce_request(
            db, tenant_id=current_user.tenant_id, purchase_request_id=request_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@purchase_requests_router.post(
    "/{request_id}/execute",
    response_model=CommerceExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Commerce Transaction",
    description="Orchestrate purchase request execution through AgentPay core transaction pipeline (Phase 184).",  # noqa: E501
    operation_id="execute_purchase_request",
    dependencies=[Depends(require_permission(PRODUCTS_UPDATE))],
)
async def execute_purchase_request(
    request_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    orchestrator: Annotated[
        CommerceTransactionOrchestratorService, Depends(get_commerce_orchestrator_service)
    ],
    idempotency_key: str | None = None,
) -> CommerceExecutionResponse:
    """Orchestrate purchase request execution."""
    try:
        req = CommerceExecutionRequest(
            purchase_request_id=request_id, idempotency_key=idempotency_key
        )
        return await orchestrator.execute_commerce_transaction(
            db, tenant_id=current_user.tenant_id, request=req, user_id=current_user.user.id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ExecutionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@purchase_requests_router.get(
    "/{request_id}/execution",
    response_model=CommerceExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Commerce Transaction Execution Status",
    description="Check orchestration execution status for a purchase request (Phase 184).",
    operation_id="get_purchase_request_execution",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_purchase_request_execution(
    request_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    orchestrator: Annotated[
        CommerceTransactionOrchestratorService, Depends(get_commerce_orchestrator_service)
    ],
) -> CommerceExecutionResponse:
    """Get purchase transaction execution status."""
    try:
        req = CommerceExecutionRequest(purchase_request_id=request_id)
        return await orchestrator.execute_commerce_transaction(
            db, tenant_id=current_user.tenant_id, request=req, user_id=current_user.user.id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@purchase_requests_router.post(
    "/{request_id}/cancel",
    response_model=CommerceExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Commerce Transaction Request",
    description="Cancel a pending purchase transaction request (Phase 184).",
    operation_id="cancel_purchase_request",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def cancel_purchase_request(
    request_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    orchestrator: Annotated[
        CommerceTransactionOrchestratorService, Depends(get_commerce_orchestrator_service)
    ],
) -> CommerceExecutionResponse:
    """Cancel pending purchase transaction."""
    try:
        return await orchestrator.cancel_commerce_transaction(
            db, tenant_id=current_user.tenant_id, purchase_request_id=request_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ExecutionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
