"""Human Approval Integration Subsystem (Phase 310)."""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Any

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.approval_workflow_service import (
    ApprovalWorkflowConflictError,
    ApprovalWorkflowError,
    ApprovalWorkflowService,
)
from app.payment.approval.approved_payment_continuation_service import (
    ApprovedPaymentContinuationError,
    ApprovedPaymentContinuationService,
)
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_audit import ApprovalAuditActorType, ApprovalAuditEventType
from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
)
from app.schemas.approved_payment_continuation import (
    ApprovedPaymentContinuationCommand,
)
from app.schemas.human_approval import (
    FORBIDDEN_AUTOMATED_IDENTITIES,
    HumanApprovalCommand,
    HumanApprovalResult,
    HumanReviewContextResponse,
    HumanReviewerContext,
)
from app.schemas.reviewer_authorization import (
    ReviewerPermission,
    TrustedReviewerContext,
)
from app.schemas.risk_engine import RiskThresholdBand

logger = logging.getLogger("agentpay.payment.approval.human_integration")


class HumanApprovalError(Exception):
    """Domain exception raised when human approval fails or is blocked by security controls."""

    def __init__(self, message: str, error_code: str = "HUMAN_APPROVAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class HumanApprovalConflictError(HumanApprovalError):
    """Domain exception raised when human approval encounters an idempotency parameter conflict."""

    def __init__(self, message: str, error_code: str = "HUMAN_APPROVAL_CONFLICT") -> None:
        super().__init__(message, error_code=error_code)


class HumanApprovalIntegrationService:
    """Production Human Approval Integration Layer (Phase 310).

    Bridges authenticated human reviewers to backend approval control plane.

    CRITICAL SECURITY INVARIANTS:
    - HUMAN REVIEWER ONLY: Automated/agent identities strictly forbidden.
    - AI AGENT != REVIEWER: Self-approval strictly rejected (reviewer_id != agent_id).
    - AUTHORITATIVE AUTHENTICATION: Server-side token/session context is trusted.
    - STRICT TENANT ISOLATION: reviewer.tenant_id == approval_request.tenant_id.
    - FINANCIAL PARAMETER IMMUTABILITY: Human reviewer cannot mutate amount/currency.
    - APPROVAL != PAYMENT SUCCESS: Approval grants permission for continuation execution.
    - ONE-TIME CONSUMPTION & IDEMPOTENCY: Idempotency keys prevent double execution.
    - THREAD-SAFE CONCURRENCY LOCK: Prevents TOCTOU race conditions.
    - ZERO RAZORPAY SDK ACCESS: Executes downstream payment strictly via provider abstraction.
    - ZERO RISK RECALCULATION & ZERO AUDIT DELETION.
    """

    def __init__(
        self,
        request_service: ApprovalRequestService | None = None,
        auth_service: ReviewerAuthorizationService | None = None,
        workflow_service: ApprovalWorkflowService | None = None,
        audit_service: ApprovalAuditService | None = None,
        continuation_service: ApprovedPaymentContinuationService | None = None,
    ) -> None:
        """Initialize Human Approval Integration Service dependencies."""
        self._audit_service = audit_service or ApprovalAuditService()
        self._request_service = request_service or ApprovalRequestService(
            audit_service=self._audit_service
        )
        self._auth_service = auth_service or ReviewerAuthorizationService()
        self._workflow_service = workflow_service or ApprovalWorkflowService(
            request_service=self._request_service,
            auth_service=self._auth_service,
            audit_service=self._audit_service,
        )
        self._continuation_service = continuation_service or ApprovedPaymentContinuationService(
            request_service=self._request_service, audit_service=self._audit_service
        )

        self._lock = threading.Lock()
        # In-memory cache for idempotency: (tenant_id, approval_request_id, idempotency_key) -> (command, result)
        self._idempotency_cache: dict[
            tuple[uuid.UUID, uuid.UUID, str], tuple[dict[str, Any], HumanApprovalResult]
        ] = {}

    def get_human_review_context(
        self,
        tenant_id: uuid.UUID,
        approval_request_id: uuid.UUID,
        reviewer_id: uuid.UUID | None = None,
    ) -> HumanReviewContextResponse | None:
        """Retrieve safe review context UX contract for human decision making (Phase 310)."""
        logger.info(
            "Fetching human review context for request=%s (tenant=%s)",
            approval_request_id,
            tenant_id,
        )
        req = self._request_service.get_approval_request(
            tenant_id=tenant_id, approval_request_id=approval_request_id
        )
        if req is None:
            return None

        # Emit audit event for review viewed
        self._audit_service.record_event(
            tenant_id=tenant_id,
            approval_request_id=approval_request_id,
            transaction_id=req.transaction_id,
            agent_id=req.agent_id,
            event_type=ApprovalAuditEventType.APPROVAL_VIEWED,
            actor_type=ApprovalAuditActorType.REVIEWER,
            actor_id=reviewer_id,
            approval_fingerprint=req.approval_fingerprint,
            metadata={
                "status": req.status.value,
                "amount": str(req.amount),
                "currency": req.currency.value,
            },
        )

        # Derive risk_band from risk_score if needed
        risk_band = (
            RiskThresholdBand.HIGH_RISK_BAND
            if req.risk_score >= 70.0
            else (
                RiskThresholdBand.MEDIUM_RISK_BAND
                if req.risk_score >= 30.0
                else RiskThresholdBand.LOW_RISK_BAND
            )
        )

        return HumanReviewContextResponse(
            approval_request_id=req.approval_request_id,
            tenant_id=req.tenant_id,
            transaction_id=req.transaction_id,
            agent_id=req.agent_id,
            amount=req.amount,
            currency=req.currency,
            risk_score=req.risk_score,
            risk_band=risk_band,
            priority=str(req.priority.value),
            status=req.status,
            approval_fingerprint=req.approval_fingerprint,
            created_at=req.created_at,
            expires_at=req.expires_at,
        )

    def execute_human_approval(
        self,
        command: HumanApprovalCommand,
        reviewer_context: HumanReviewerContext,
    ) -> HumanApprovalResult:
        """Execute production human approval flow (Phase 310)."""
        logger.info(
            "Executing human approval for req=%s by reviewer=%s (tenant=%s)",
            command.approval_request_id,
            reviewer_context.reviewer_id,
            command.tenant_id,
        )

        with self._lock:
            # 1. Enforce Human Identity Verification
            if not reviewer_context.is_human_verified:
                raise HumanApprovalError(
                    "Reviewer identity must be human-verified.",
                    error_code="REVIEWER_NOT_HUMAN",
                )

            # 2. Strict Tenant Isolation
            if command.tenant_id != reviewer_context.tenant_id:
                raise HumanApprovalError(
                    "Reviewer tenant ID does not match request tenant ID.",
                    error_code="CROSS_TENANT_ACCESS",
                )

            # 3. Idempotency Cache Check (Before Request Status Lookup!)
            cache_key = (command.tenant_id, command.approval_request_id, command.idempotency_key)
            if cache_key in self._idempotency_cache:
                stored_cmd, stored_res = self._idempotency_cache[cache_key]

                # Verify fingerprint & key parameter match
                if (
                    stored_cmd["expected_approval_fingerprint"]
                    != command.expected_approval_fingerprint
                    or stored_cmd["auto_continue"] != command.auto_continue
                    or stored_cmd.get("reviewer_comment") != command.reviewer_comment
                ):
                    raise HumanApprovalConflictError(
                        f"Idempotency key '{command.idempotency_key}' reused with modified parameters."
                    )

                logger.info(
                    f"Human approval IDEMPOTENT REPLAY for req={command.approval_request_id} (key={command.idempotency_key})"
                )
                return stored_res.model_copy(update={"is_existing": True})

            # 4. Load Target Approval Request
            req = self._request_service.get_approval_request(
                tenant_id=command.tenant_id, approval_request_id=command.approval_request_id
            )
            if req is None:
                raise HumanApprovalError(
                    f"Approval request '{command.approval_request_id}' not found.",
                    error_code="APPROVAL_REQUEST_NOT_FOUND",
                )

            # Database-Authoritative Check: Handle cross-worker / multi-process idempotency replay & terminal state guard
            if req.status != ApprovalRequestStatus.PENDING:
                if req.status == ApprovalRequestStatus.APPROVED:
                    if command.expected_approval_fingerprint != req.approval_fingerprint:
                        raise HumanApprovalConflictError(
                            f"Idempotency key '{command.idempotency_key}' reused with modified parameters."
                        )
                    return HumanApprovalResult(
                        approval_request_id=req.approval_request_id,
                        tenant_id=req.tenant_id,
                        reviewer_id=reviewer_context.reviewer_id,
                        transaction_id=req.transaction_id,
                        status=ApprovalRequestStatus.APPROVED,
                        decision=ApprovalDecisionType.APPROVE,
                        decision_fingerprint=req.approval_fingerprint,
                        continuation_status="CONTINUATION_EXECUTED" if command.auto_continue else None,
                        is_existing=True,
                    )
                raise HumanApprovalError(
                    f"Approval request '{command.approval_request_id}' status is "
                    f"'{req.status.value}'. Cannot transition to APPROVED.",
                    error_code="INVALID_STATE_TRANSITION",
                )

            # 5. Self-Approval Protection (Agent cannot be Reviewer!)
            if reviewer_context.reviewer_id == req.agent_id:
                self._audit_service.record_event(
                    tenant_id=command.tenant_id,
                    approval_request_id=command.approval_request_id,
                    transaction_id=req.transaction_id,
                    agent_id=req.agent_id,
                    event_type=ApprovalAuditEventType.APPROVAL_AUTHORIZATION_FAILED,
                    actor_type=ApprovalAuditActorType.REVIEWER,
                    actor_id=reviewer_context.reviewer_id,
                    approval_fingerprint=req.approval_fingerprint,
                    metadata={"reason": "SELF_APPROVAL_FORBIDDEN", "agent_id": str(req.agent_id)},
                )
                raise HumanApprovalError(
                    f"Reviewer '{reviewer_context.reviewer_id}' is the originating agent. Self-approval is forbidden.",
                    error_code="SELF_APPROVAL_FORBIDDEN",
                )

            # 6. Automated / Non-Human Identity Check
            str_reviewer_id = str(reviewer_context.reviewer_id).lower()
            if str_reviewer_id in FORBIDDEN_AUTOMATED_IDENTITIES:
                raise HumanApprovalError(
                    f"Automated identity '{reviewer_context.reviewer_id}' cannot act as a human reviewer.",
                    error_code="AUTOMATED_REVIEWER_FORBIDDEN",
                )

            if reviewer_context.reviewer_email:
                email_prefix = reviewer_context.reviewer_email.split("@")[0].lower()
                if any(auto_str in email_prefix for auto_str in FORBIDDEN_AUTOMATED_IDENTITIES):
                    raise HumanApprovalError(
                        f"Automated email identity '{reviewer_context.reviewer_email}' forbidden.",
                        error_code="AUTOMATED_REVIEWER_FORBIDDEN",
                    )

            # 6. Build TrustedReviewerContext for Authorizer
            trusted_auth_ctx = TrustedReviewerContext(
                reviewer_id=reviewer_context.reviewer_id,
                tenant_id=reviewer_context.tenant_id,
                reviewer_role=reviewer_context.reviewer_role,
                permissions=(
                    reviewer_context.permissions
                    if reviewer_context.permissions
                    else {ReviewerPermission.APPROVE_PAYMENT}
                ),
                session_id=reviewer_context.session_id,
                authenticated_at=reviewer_context.authenticated_at,
                authorization_limit=reviewer_context.authorization_limit,
            )

            # 7. Execute Approval Transition via ApprovalWorkflowService
            workflow_cmd = ApprovalDecisionCommand(
                approval_request_id=command.approval_request_id,
                tenant_id=command.tenant_id,
                reviewer_context=trusted_auth_ctx,
                decision=ApprovalDecisionType.APPROVE,
                reviewer_comment=command.reviewer_comment,
                idempotency_key=command.idempotency_key,
                expected_approval_fingerprint=command.expected_approval_fingerprint,
            )

            try:
                workflow_res = self._workflow_service.approve_request(workflow_cmd)
            except ApprovalWorkflowConflictError as exc:
                raise HumanApprovalConflictError(
                    exc.message, error_code="HUMAN_APPROVAL_CONFLICT"
                ) from exc
            except ApprovalWorkflowError as exc:
                raise HumanApprovalError(exc.message, error_code=exc.error_code) from exc

            # 8. Post-Approval Payment Continuation (Phase 309 Integration)
            continuation_status: str | None = None
            if command.auto_continue:
                cont_cmd = ApprovedPaymentContinuationCommand(
                    approval_request_id=command.approval_request_id,
                    tenant_id=command.tenant_id,
                    agent_id=req.agent_id,
                    transaction_id=req.transaction_id,
                    amount=req.amount,
                    currency=req.currency,
                    idempotency_key=f"cont-{command.idempotency_key}",
                    expected_approval_fingerprint=command.expected_approval_fingerprint,
                )

                try:
                    cont_res = self._continuation_service.execute_continuation(cont_cmd)
                    continuation_status = cont_res.execution_status
                except ApprovedPaymentContinuationError as cont_exc:
                    logger.error(
                        "Approved payment continuation failed post-human approval for req=%s: %s",
                        command.approval_request_id,
                        cont_exc.message,
                    )
                    continuation_status = f"CONTINUATION_FAILED: {cont_exc.error_code}"

            # 9. Construct Final HumanApprovalResult
            final_res = HumanApprovalResult(
                approval_request_id=workflow_res.approval_request_id,
                tenant_id=workflow_res.tenant_id,
                reviewer_id=workflow_res.reviewer_id,
                transaction_id=req.transaction_id,
                status=ApprovalRequestStatus.APPROVED,
                decision=ApprovalDecisionType.APPROVE,
                decision_fingerprint=workflow_res.decision_fingerprint,
                continuation_status=continuation_status,
                is_existing=False,
            )

            # Store in idempotency cache
            self._idempotency_cache[cache_key] = (
                {
                    "expected_approval_fingerprint": command.expected_approval_fingerprint,
                    "auto_continue": command.auto_continue,
                },
                final_res,
            )

            logger.info(
                "Human approval EXECUTED SUCCESSFUL for req=%s (continuation=%s)",
                command.approval_request_id,
                continuation_status,
            )
            return final_res
