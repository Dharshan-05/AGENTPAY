"""Risk & Decision Engine REST Controller Router (Phases 283-284)."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.risk_decision_service import RiskDecisionApplicationService
from app.domain.authorization.permissions_registry import (
    RISK_DECISIONS_EVALUATE,
    RISK_DECISIONS_READ,
)
from app.schemas.risk_decision_api import (
    RiskDecisionEvaluateRequest,
    RiskDecisionEvaluateResponse,
)
from app.schemas.risk_engine import DecisionAuditEvent

logger = logging.getLogger("agentpay.api.v1.risk_decisions")

risk_decisions_router = APIRouter(prefix="/risk-decisions", tags=["Risk & Decision Engine"])


_risk_decision_service = RiskDecisionApplicationService()


def get_risk_decision_service() -> RiskDecisionApplicationService:
    """Dependency factory for RiskDecisionApplicationService."""
    return _risk_decision_service


@risk_decisions_router.post(
    "/evaluate",
    response_model=RiskDecisionEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Authoritative Risk Decision",
    description="Execute complete Risk & Decision Engine pipeline, explanation engine, and audit event recording (Phase 284).",  # noqa: E501
    operation_id="evaluate_risk_decision",
    dependencies=[Depends(require_permission(RISK_DECISIONS_EVALUATE))],
)
async def evaluate_risk_decision(
    request: RiskDecisionEvaluateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[RiskDecisionApplicationService, Depends(get_risk_decision_service)],
) -> RiskDecisionEvaluateResponse:
    """Evaluate authoritative risk decision under authenticated tenant scope."""
    try:
        return service.evaluate_risk_decision(current_user.tenant_id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@risk_decisions_router.get(
    "/audit/{decision_id}",
    response_model=DecisionAuditEvent,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Decision Audit Event",
    description="Retrieve append-only decision audit event record by decision ID under tenant isolation (Phase 283).",  # noqa: E501
    operation_id="get_decision_audit_event",
    dependencies=[Depends(require_permission(RISK_DECISIONS_READ))],
)
async def get_decision_audit_event(
    decision_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[RiskDecisionApplicationService, Depends(get_risk_decision_service)],
) -> DecisionAuditEvent:
    """Retrieve decision audit event under tenant isolation."""
    event = service.get_audit_event(current_user.tenant_id, decision_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision audit event '{decision_id}' not found.",
        )
    return event
