"""FastAPI Payment Approvals API Router Boundary (Phases 304–307)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_expiration_service import (
    ApprovalExpirationError,
    ApprovalExpirationService,
)
from app.payment.approval.approval_rejection_service import (
    ApprovalRejectionConflictError,
    ApprovalRejectionError,
    ApprovalRejectionService,
)
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import (
    ApprovalWorkflowConflictError,
    ApprovalWorkflowError,
    ApprovalWorkflowService,
)
from app.payment.approval.approved_payment_continuation_service import (
    ApprovedPaymentContinuationConflictError,
    ApprovedPaymentContinuationError,
    ApprovedPaymentContinuationService,
)
from app.payment.approval.human_approval_service import (
    HumanApprovalConflictError,
    HumanApprovalError,
    HumanApprovalIntegrationService,
)
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_audit import ApprovalAuditQueryResult
from app.schemas.approval_expiration import ApprovalExpirationResult
from app.schemas.approval_rejection import (
    ApprovalRejectionCommand,
    ApprovalRejectionResult,
    RejectionReason,
)
from app.schemas.approval_request import ApprovalRequestRecord
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
    ApprovalWorkflowResult,
)
from app.schemas.approved_payment_continuation import (
    ApprovedPaymentContinuationCommand,
    ApprovedPaymentContinuationResult,
)
from app.schemas.human_approval import (
    HumanApprovalCommand,
    HumanApprovalResult,
    HumanReviewContextResponse,
    HumanReviewerContext,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
    ReviewerPermission,
    ReviewerRole,
    TrustedReviewerContext,
)

logger = logging.getLogger("agentpay.api.v1.approvals")

approvals_router = APIRouter(prefix="/payments/approvals", tags=["Payment Approvals"])

_audit_service = ApprovalAuditService()
_request_service = ApprovalRequestService(audit_service=_audit_service)
_auth_service = ReviewerAuthorizationService()
_workflow_service = ApprovalWorkflowService(
    request_service=_request_service, auth_service=_auth_service, audit_service=_audit_service
)
_rejection_service = ApprovalRejectionService(
    request_service=_request_service, auth_service=_auth_service, audit_service=_audit_service
)
_expiration_service = ApprovalExpirationService(
    request_service=_request_service, audit_service=_audit_service
)
_continuation_service = ApprovedPaymentContinuationService(
    request_service=_request_service, audit_service=_audit_service
)
_human_service = HumanApprovalIntegrationService(
    request_service=_request_service,
    auth_service=_auth_service,
    workflow_service=_workflow_service,
    audit_service=_audit_service,
    continuation_service=_continuation_service,
)


class ApprovalDecisionApiRequest(BaseModel):
    """API Request payload to approve an approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approval request"
    )
    reviewer_comment: str | None = Field(
        default=None, description="Optional reviewer comment (Max 500 chars)"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")


class ApprovalRejectionApiRequest(BaseModel):
    """API Request payload to reject an approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approval request"
    )
    rejection_reason: RejectionReason = Field(..., description="Categorized rejection reason")
    reviewer_comment: str | None = Field(
        default=None, description="Optional reviewer comment (Max 500 chars)"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")


@approvals_router.get(
    "/{approval_request_id}",
    response_model=ApprovalRequestRecord,
    status_code=status.HTTP_200_OK,
    summary="Get Approval Request Context (Phases 302–304)",
    description="Retrieves approval request metadata enforcing strict tenant isolation.",
)
async def get_approval_request(
    approval_request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> ApprovalRequestRecord:
    """Retrieve approval request details enforcing tenant isolation."""
    req = _request_service.get_approval_request(
        tenant_id=current_user.tenant_id, approval_request_id=approval_request_id
    )
    if req is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )
    return req


@approvals_router.post(
    "/{approval_request_id}/approve",
    response_model=ApprovalWorkflowResult,
    status_code=status.HTTP_200_OK,
    summary="Approve Payment Approval Request (Phase 305)",
    description=(
        "Executes state transition PENDING -> APPROVED for a payment approval request. "
        "Enforces reviewer authorization, self-approval prevention, monetary limits, "
        "and idempotency. DOES NOT execute downstream payment or Razorpay calls."
    ),
)
async def approve_payment_request(
    approval_request_id: uuid.UUID,
    payload: ApprovalDecisionApiRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
    x_reviewer_role: str | None = Header(default="REVIEWER", alias="X-Reviewer-Role"),
) -> ApprovalWorkflowResult:
    """Approve payment approval request enforcing Phase 304 & 305 boundaries."""
    try:
        role_enum = ReviewerRole(x_reviewer_role.upper() if x_reviewer_role else "REVIEWER")
    except ValueError:
        role_enum = ReviewerRole.REVIEWER

    reviewer_ctx = TrustedReviewerContext(
        reviewer_id=current_user.user.id,
        tenant_id=current_user.tenant_id,
        reviewer_role=role_enum,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.VIEW_REVIEW_QUEUE,
            ReviewerPermission.APPROVE_PAYMENT,
        },
    )

    cmd = ApprovalDecisionCommand(
        approval_request_id=approval_request_id,
        tenant_id=current_user.tenant_id,
        reviewer_context=reviewer_ctx,
        decision=ApprovalDecisionType.APPROVE,
        reviewer_comment=payload.reviewer_comment,
        idempotency_key=payload.idempotency_key,
        expected_approval_fingerprint=payload.expected_approval_fingerprint,
    )

    try:
        res = _workflow_service.approve_request(cmd)
        return res
    except ApprovalWorkflowConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err.message,
        ) from err
    except ApprovalWorkflowError as err:
        error_status_map: dict[str, int] = {
            "CROSS_TENANT_ACCESS": status.HTTP_404_NOT_FOUND,
            "APPROVAL_REQUEST_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "SELF_APPROVAL_FORBIDDEN": status.HTTP_403_FORBIDDEN,
            "REVIEWER_PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
            "APPROVAL_LIMIT_EXCEEDED": status.HTTP_403_FORBIDDEN,
            "ALREADY_APPROVED": status.HTTP_409_CONFLICT,
            "INVALID_STATE_TRANSITION": status.HTTP_400_BAD_REQUEST,
            "APPROVAL_FINGERPRINT_MISMATCH": status.HTTP_400_BAD_REQUEST,
        }
        status_code = error_status_map.get(err.error_code, status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=err.message) from err


@approvals_router.post(
    "/{approval_request_id}/reject",
    response_model=ApprovalRejectionResult,
    status_code=status.HTTP_200_OK,
    summary="Reject Payment Approval Request (Phase 306)",
    description=(
        "Executes state transition PENDING -> REJECTED for a payment approval request. "
        "Enforces reviewer authorization, self-rejection prevention, and idempotency. "
        "DOES NOT execute downstream payment or Razorpay calls."
    ),
)
async def reject_payment_request(
    approval_request_id: uuid.UUID,
    payload: ApprovalRejectionApiRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
    x_reviewer_role: str | None = Header(default="REVIEWER", alias="X-Reviewer-Role"),
) -> ApprovalRejectionResult:
    """Reject payment approval request enforcing Phase 304 & 306 boundaries."""
    try:
        role_enum = ReviewerRole(x_reviewer_role.upper() if x_reviewer_role else "REVIEWER")
    except ValueError:
        role_enum = ReviewerRole.REVIEWER

    reviewer_ctx = TrustedReviewerContext(
        reviewer_id=current_user.user.id,
        tenant_id=current_user.tenant_id,
        reviewer_role=role_enum,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.VIEW_REVIEW_QUEUE,
            ReviewerPermission.REJECT_PAYMENT,
        },
    )

    cmd = ApprovalRejectionCommand(
        approval_request_id=approval_request_id,
        tenant_id=current_user.tenant_id,
        reviewer_context=reviewer_ctx,
        rejection_reason=payload.rejection_reason,
        reviewer_comment=payload.reviewer_comment,
        idempotency_key=payload.idempotency_key,
        expected_approval_fingerprint=payload.expected_approval_fingerprint,
    )

    try:
        res = _rejection_service.reject_request(cmd)
        return res
    except ApprovalRejectionConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err.message,
        ) from err
    except ApprovalRejectionError as err:
        error_status_map: dict[str, int] = {
            "CROSS_TENANT_ACCESS": status.HTTP_404_NOT_FOUND,
            "APPROVAL_REQUEST_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "SELF_APPROVAL_FORBIDDEN": status.HTTP_403_FORBIDDEN,
            "REVIEWER_PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
            "APPROVAL_LIMIT_EXCEEDED": status.HTTP_403_FORBIDDEN,
            "ALREADY_REJECTED": status.HTTP_409_CONFLICT,
            "INVALID_STATE_TRANSITION": status.HTTP_400_BAD_REQUEST,
            "APPROVAL_FINGERPRINT_MISMATCH": status.HTTP_400_BAD_REQUEST,
        }
        status_code = error_status_map.get(err.error_code, status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=err.message) from err


@approvals_router.post(
    "/{approval_request_id}/expire",
    response_model=ApprovalExpirationResult,
    status_code=status.HTTP_200_OK,
    summary="Expire Overdue Payment Approval Request (Phase 307)",
    description=(
        "Evaluates server-authoritative UTC deadline and executes PENDING -> EXPIRED "
        "state transition if overdue. Idempotent and thread-safe. Cannot overwrite terminal states."
    ),
)
async def expire_payment_request(
    approval_request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> ApprovalExpirationResult:
    """Expire payment approval request enforcing Phase 307 boundaries."""
    try:
        res = _expiration_service.expire_approval_request(
            approval_request_id=approval_request_id,
            tenant_id=current_user.tenant_id,
        )
        return res
    except ApprovalExpirationError as err:
        error_status_map: dict[str, int] = {
            "APPROVAL_REQUEST_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        }
        status_code = error_status_map.get(err.error_code, status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=err.message) from err


@approvals_router.get(
    "/{approval_request_id}/audit",
    response_model=ApprovalAuditQueryResult,
    status_code=status.HTTP_200_OK,
    summary="Get Approval Request Audit Log (Phase 308)",
    description=(
        "Retrieves immutable, tamper-evident audit log for an approval "
        "request enforcing tenant isolation."
    ),
)
async def get_approval_request_audit(
    approval_request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> ApprovalAuditQueryResult:
    """Retrieve approval request audit history enforcing Phase 308 boundaries."""
    return _audit_service.get_audit_events_for_request(
        tenant_id=current_user.tenant_id,
        approval_request_id=approval_request_id,
    )


class ApprovedPaymentContinuationApiRequest(BaseModel):
    """API Request payload to continue payment execution post-approval (Phase 309)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_id: uuid.UUID = Field(..., description="Originating agent ID")
    transaction_id: str = Field(..., description="Target transaction ID")
    amount: Decimal = Field(..., description="Approved payment amount")
    currency: SupportedCurrency = Field(..., description="Approved currency")
    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approved request"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")


@approvals_router.post(
    "/{approval_request_id}/continue",
    response_model=ApprovedPaymentContinuationResult,
    status_code=status.HTTP_200_OK,
    summary="Continue Payment Execution Post-Approval (Phase 309)",
    description=(
        "Executes downstream payment initiation ONLY AFTER human approval "
        "(Phase 305) has been granted. Enforces approval fingerprint "
        "re-validation, financial parameter immutability, one-time "
        "approval consumption, and idempotency."
    ),
)
async def continue_approved_payment(
    approval_request_id: uuid.UUID,
    payload: ApprovedPaymentContinuationApiRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> ApprovedPaymentContinuationResult:
    """Continue payment execution for an approved approval request (Phase 309)."""
    cmd = ApprovedPaymentContinuationCommand(
        approval_request_id=approval_request_id,
        tenant_id=current_user.tenant_id,
        agent_id=payload.agent_id,
        transaction_id=payload.transaction_id,
        amount=payload.amount,
        currency=payload.currency,
        idempotency_key=payload.idempotency_key,
        expected_approval_fingerprint=payload.expected_approval_fingerprint,
    )

    try:
        res = _continuation_service.execute_continuation(cmd)
        return res
    except ApprovedPaymentContinuationConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err.message,
        ) from err
    except ApprovedPaymentContinuationError as err:
        error_status_map: dict[str, int] = {
            "APPROVAL_REQUEST_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "APPROVAL_NOT_APPROVED": status.HTTP_400_BAD_REQUEST,
            "FINANCIAL_PARAMETER_TAMPERING": status.HTTP_400_BAD_REQUEST,
        }
        status_code = error_status_map.get(err.error_code, status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=err.message) from err


class HumanApprovalApiRequest(BaseModel):
    """API Request payload for human payment approval (Phase 310)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approval request"
    )
    reviewer_comment: str | None = Field(
        default=None, description="Optional reviewer comment (Max 500 chars)"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")
    auto_continue: bool = Field(
        default=True, description="Trigger Phase 309 approved payment continuation"
    )


@approvals_router.get(
    "/{approval_request_id}/review",
    response_model=HumanReviewContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Human Review UX Context (Phase 310)",
    description=(
        "Retrieves safe, non-sensitive approval request metadata formatted for human "
        "reviewers enforcing tenant isolation."
    ),
)
async def get_human_review_context(
    approval_request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> HumanReviewContextResponse:
    """Retrieve safe human review UX metadata (Phase 310)."""
    res = _human_service.get_human_review_context(
        tenant_id=current_user.tenant_id,
        approval_request_id=approval_request_id,
        reviewer_id=current_user.user.id,
    )
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )
    return res


@approvals_router.post(
    "/{approval_request_id}/human-approve",
    response_model=HumanApprovalResult,
    status_code=status.HTTP_200_OK,
    summary="Execute Human Payment Approval (Phase 310)",
    description=(
        "Executes end-to-end human reviewer payment approval connecting authenticated "
        "human identity to ReviewerAuthorization, ApprovalWorkflow, ApprovalAudit, "
        "and ApprovedPaymentContinuation."
    ),
)
async def execute_human_approval(
    approval_request_id: uuid.UUID,
    payload: HumanApprovalApiRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
    x_reviewer_role: str | None = Header(default="REVIEWER", alias="X-Reviewer-Role"),
) -> HumanApprovalResult:
    """Execute human approval flow enforcing Phase 310 boundaries."""
    try:
        role_enum = ReviewerRole(x_reviewer_role.upper() if x_reviewer_role else "REVIEWER")
    except ValueError:
        role_enum = ReviewerRole.REVIEWER

    human_ctx = HumanReviewerContext(
        reviewer_id=current_user.user.id,
        tenant_id=current_user.tenant_id,
        reviewer_email=getattr(current_user.user, "email", None),
        reviewer_role=role_enum,
        permissions={
            ReviewerPermission.VIEW_APPROVAL_REQUEST,
            ReviewerPermission.VIEW_REVIEW_QUEUE,
            ReviewerPermission.APPROVE_PAYMENT,
        },
        session_id=str(current_user.session.id) if current_user.session else None,
        is_human_verified=True,
    )

    cmd = HumanApprovalCommand(
        approval_request_id=approval_request_id,
        tenant_id=current_user.tenant_id,
        expected_approval_fingerprint=payload.expected_approval_fingerprint,
        reviewer_comment=payload.reviewer_comment,
        idempotency_key=payload.idempotency_key,
        auto_continue=payload.auto_continue,
    )

    try:
        return _human_service.execute_human_approval(cmd, human_ctx)
    except HumanApprovalConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=err.message,
        ) from err
    except HumanApprovalError as err:
        error_status_map: dict[str, int] = {
            "CROSS_TENANT_ACCESS": status.HTTP_404_NOT_FOUND,
            "APPROVAL_REQUEST_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "SELF_APPROVAL_FORBIDDEN": status.HTTP_403_FORBIDDEN,
            "REVIEWER_PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
            "AUTOMATED_REVIEWER_FORBIDDEN": status.HTTP_403_FORBIDDEN,
            "REVIEWER_NOT_HUMAN": status.HTTP_403_FORBIDDEN,
            "APPROVAL_LIMIT_EXCEEDED": status.HTTP_403_FORBIDDEN,
            "INVALID_STATE_TRANSITION": status.HTTP_400_BAD_REQUEST,
            "APPROVAL_FINGERPRINT_MISMATCH": status.HTTP_400_BAD_REQUEST,
        }
        status_code = error_status_map.get(err.error_code, status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=err.message) from err
