"""FraudGuard ML, Risk & XAI REST Controller Router (Phases 261-265)."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.fraudguard_service import FraudGuardApplicationService
from app.domain.authorization.permissions_registry import (
    FRAUDGUARD_EVALUATE,
    FRAUDGUARD_INFER,
    FRAUDGUARD_RISK_READ,
    FRAUDGUARD_XAI_READ,
)
from app.schemas.fraudguard_api import (
    FraudGuardEvaluateRequest,
    FraudGuardEvaluateResponse,
    FraudGuardGlobalXAIRequest,
    FraudGuardInferenceRequest,
    FraudGuardInferenceResponse,
    FraudGuardLocalXAIRequest,
    FraudGuardRiskIntelligenceRequest,
    FraudGuardRiskIntelligenceResponse,
)
from app.schemas.ml_xai import GlobalModelExplanation, LocalTransactionExplanation

logger = logging.getLogger("fraudguard.api.router")

fraudguard_router = APIRouter(prefix="/fraudguard", tags=["FraudGuard - ML & Risk Intelligence"])


def get_fraudguard_service() -> FraudGuardApplicationService:
    """Dependency factory for FraudGuardApplicationService."""
    return FraudGuardApplicationService()


@fraudguard_router.post(
    "/inference",
    response_model=FraudGuardInferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Real-Time FraudGuard ML Inference",
    description="Execute real-time XGBoost inference on production model artifact (Phase 263).",
    operation_id="run_fraudguard_inference",
    dependencies=[Depends(require_permission(FRAUDGUARD_INFER))],
)
async def run_inference(
    request: FraudGuardInferenceRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[FraudGuardApplicationService, Depends(get_fraudguard_service)],
) -> FraudGuardInferenceResponse:
    """Execute real-time FraudGuard inference under tenant scope."""
    return service.run_inference(current_user.tenant_id, request)


@fraudguard_router.post(
    "/risk-intelligence",
    response_model=FraudGuardRiskIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute FraudGuard Risk Intelligence Pipeline",
    description="Execute complete risk scoring pipeline including merchant, velocity, intent & policy risk (Phase 264).",  # noqa: E501
    operation_id="run_fraudguard_risk_intelligence",
    dependencies=[Depends(require_permission(FRAUDGUARD_RISK_READ))],
)
async def run_risk_intelligence(
    request: FraudGuardRiskIntelligenceRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[FraudGuardApplicationService, Depends(get_fraudguard_service)],
) -> FraudGuardRiskIntelligenceResponse:
    """Execute risk intelligence pipeline under tenant scope."""
    return service.run_risk_intelligence(current_user.tenant_id, request)


@fraudguard_router.post(
    "/xai/local-explanation",
    response_model=LocalTransactionExplanation,
    status_code=status.HTTP_200_OK,
    summary="Generate Local Transaction XAI Explanation",
    description="Generate model-version-bound SHAP feature attributions and non-causal explanation (Phase 261).",  # noqa: E501
    operation_id="generate_fraudguard_local_xai",
    dependencies=[Depends(require_permission(FRAUDGUARD_XAI_READ))],
)
async def generate_local_xai(
    request: FraudGuardLocalXAIRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[FraudGuardApplicationService, Depends(get_fraudguard_service)],
) -> LocalTransactionExplanation:
    """Generate local transaction XAI explanation under tenant scope."""
    return service.generate_local_xai(current_user.tenant_id, request)


@fraudguard_router.post(
    "/xai/global-explanation",
    response_model=GlobalModelExplanation,
    status_code=status.HTTP_200_OK,
    summary="Generate Global Model XAI Explanation",
    description="Generate aggregate global feature importance over target-free dataset (Phase 261).",  # noqa: E501
    operation_id="generate_fraudguard_global_xai",
    dependencies=[Depends(require_permission(FRAUDGUARD_XAI_READ))],
)
async def generate_global_xai(
    request: FraudGuardGlobalXAIRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[FraudGuardApplicationService, Depends(get_fraudguard_service)],
) -> GlobalModelExplanation:
    """Generate global model XAI explanation under tenant scope."""
    return service.generate_global_xai(current_user.tenant_id, request)


@fraudguard_router.post(
    "/evaluate",
    response_model=FraudGuardEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Unified End-to-End FraudGuard Evaluation",
    description="Execute unified end-to-end evaluation enforcing authoritative policy DENY precedence (Phase 265).",  # noqa: E501
    operation_id="evaluate_fraudguard_transaction",
    dependencies=[Depends(require_permission(FRAUDGUARD_EVALUATE))],
)
async def evaluate_transaction(
    request: FraudGuardEvaluateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[FraudGuardApplicationService, Depends(get_fraudguard_service)],
) -> FraudGuardEvaluateResponse:
    """Execute end-to-end FraudGuard evaluation under tenant scope."""
    return service.evaluate_transaction(current_user.tenant_id, request)
