"""Approval Workflow Subsystem (Phase 305)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from datetime import UTC, datetime

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.reviewer_authorization_service import ReviewerAuthorizationService
from app.schemas.approval_audit import ApprovalAuditActorType, ApprovalAuditEventType
from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.approval_workflow import (
    ApprovalDecisionCommand,
    ApprovalDecisionType,
    ApprovalWorkflowResult,
)
from app.schemas.reviewer_authorization import ReviewerPermission

logger = logging.getLogger("agentpay.payment.approval.workflow")


class ApprovalWorkflowError(Exception):
    """Domain exception raised when an approval workflow transition fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_WORKFLOW_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalWorkflowConflictError(ApprovalWorkflowError):
    """Raised when an idempotency key is reused with modified parameters (409)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="APPROVAL_WORKFLOW_CONFLICT")


class ApprovalWorkflowService:
    """Production Approval Workflow Service (Phase 305).

    Primary responsibility: Execute state transition PENDING -> APPROVED
    when ALL authorization controls succeed.
    """

    def __init__(
        self,
        request_service: ApprovalRequestService,
        auth_service: ReviewerAuthorizationService,
        audit_service: ApprovalAuditService | None = None,
    ) -> None:
        self.request_service = request_service
        self.auth_service = auth_service
        self.audit_service = audit_service or ApprovalAuditService()
        # In-memory thread-safe store for executed approval workflow results & idempotency
        self._store_by_idempotency: dict[str, tuple[ApprovalWorkflowResult, str]] = {}
        self._lock = threading.Lock()

    def approve_request(self, command: ApprovalDecisionCommand) -> ApprovalWorkflowResult:
        """Execute state transition PENDING -> APPROVED (Phase 305)."""
        logger.info(
            "ApprovalWorkflowService executing APPROVE for request=%s (tenant=%s, reviewer=%s)",
            command.approval_request_id,
            command.tenant_id,
            command.reviewer_context.reviewer_id,
        )

        # 1. Decision Guard: Phase 305 strictly handles APPROVE
        if command.decision != ApprovalDecisionType.APPROVE:
            raise ApprovalWorkflowError(
                f"Unsupported decision type '{command.decision.value}'. "
                "Phase 305 handles APPROVE decisions only.",
                error_code="UNSUPPORTED_DECISION_TYPE",
            )

        # 2. Idempotency Key & Parameter Fingerprint Computation
        idemp_identity = (
            f"{command.tenant_id}|{command.reviewer_context.reviewer_id}|"
            f"{command.approval_request_id}|{command.idempotency_key}"
        )
        param_fp = self._calculate_command_fingerprint(command)

        with self._lock:
            # 3. Check Idempotency Store
            if idemp_identity in self._store_by_idempotency:
                existing_res, stored_fp = self._store_by_idempotency[idemp_identity]
                if stored_fp != param_fp:
                    raise ApprovalWorkflowConflictError(
                        "Approval idempotency key reused with modified parameters!"
                    )
                return ApprovalWorkflowResult(
                    approval_request_id=existing_res.approval_request_id,
                    tenant_id=existing_res.tenant_id,
                    reviewer_id=existing_res.reviewer_id,
                    previous_status=existing_res.previous_status,
                    new_status=existing_res.new_status,
                    decision=existing_res.decision,
                    decision_fingerprint=existing_res.decision_fingerprint,
                    is_existing=True,
                    approved_at=existing_res.approved_at,
                )

            # 4. Lookup Authoritative Approval Request
            approval_request = self.request_service.get_approval_request(
                tenant_id=command.tenant_id,
                approval_request_id=command.approval_request_id,
            )

            if approval_request is None:
                raise ApprovalWorkflowError(
                    f"Approval request '{command.approval_request_id}' not found.",
                    error_code="APPROVAL_REQUEST_NOT_FOUND",
                )

            # 5. State Machine Transition Guard: Must be PENDING
            if approval_request.status == ApprovalRequestStatus.APPROVED:
                raise ApprovalWorkflowError(
                    f"Approval request '{command.approval_request_id}' is ALREADY_APPROVED.",
                    error_code="ALREADY_APPROVED",
                )

            if approval_request.status != ApprovalRequestStatus.PENDING:
                raise ApprovalWorkflowError(
                    f"Cannot transition status '{approval_request.status.value}' to APPROVED.",
                    error_code="INVALID_STATE_TRANSITION",
                )

            # 6. Evaluate Reviewer Authorization (Phase 304 Integration)
            auth_res = self.auth_service.authorize_reviewer(
                reviewer_context=command.reviewer_context,
                approval_request=approval_request,
                required_permission=ReviewerPermission.APPROVE_PAYMENT,
                expected_approval_fingerprint=command.expected_approval_fingerprint,
            )

            if not auth_res.authorized:
                raise ApprovalWorkflowError(
                    f"Reviewer authorization DENIED: {auth_res.reason_code}",
                    error_code=auth_res.reason_code,
                )

            # 7. Atomic TOCTOU State Mutation under Lock
            # Mutate status from PENDING -> APPROVED on the underlying approval request record
            now_utc = datetime.now(UTC)
            updated_record = approval_request.model_copy(
                update={"status": ApprovalRequestStatus.APPROVED}
            )
            # Update request in service internal store
            self.request_service._store_by_id[updated_record.approval_request_id] = updated_record

            # 8. Compute Decision Fingerprint
            dec_fp = self._calculate_decision_fingerprint(
                original_fingerprint=approval_request.approval_fingerprint,
                reviewer_id=command.reviewer_context.reviewer_id,
                tenant_id=command.tenant_id,
                approval_request_id=command.approval_request_id,
                timestamp=now_utc,
            )

            result = ApprovalWorkflowResult(
                approval_request_id=command.approval_request_id,
                tenant_id=command.tenant_id,
                reviewer_id=command.reviewer_context.reviewer_id,
                previous_status=ApprovalRequestStatus.PENDING,
                new_status=ApprovalRequestStatus.APPROVED,
                decision=ApprovalDecisionType.APPROVE,
                decision_fingerprint=dec_fp,
                is_existing=False,
                approved_at=now_utc,
            )

            self._store_by_idempotency[idemp_identity] = (result, param_fp)

            # Record Audit Event (Phase 308)
            self.audit_service.record_event(
                tenant_id=approval_request.tenant_id,
                approval_request_id=approval_request.approval_request_id,
                transaction_id=approval_request.transaction_id,
                agent_id=approval_request.agent_id,
                event_type=ApprovalAuditEventType.APPROVAL_APPROVED,
                actor_type=ApprovalAuditActorType.REVIEWER,
                actor_id=command.reviewer_context.reviewer_id,
                previous_status=ApprovalRequestStatus.PENDING,
                resulting_status=ApprovalRequestStatus.APPROVED,
                approval_fingerprint=approval_request.approval_fingerprint,
                metadata={"decision_fingerprint": dec_fp},
            )

        logger.info(
            "Approval request %s SUCCESSFUL state transition PENDING -> APPROVED by reviewer %s",
            command.approval_request_id,
            command.reviewer_context.reviewer_id,
        )

        return result

    def _calculate_command_fingerprint(self, command: ApprovalDecisionCommand) -> str:
        """Calculate fingerprint over command payload for idempotency detection."""
        payload = {
            "approval_request_id": str(command.approval_request_id),
            "tenant_id": str(command.tenant_id),
            "reviewer_id": str(command.reviewer_context.reviewer_id),
            "decision": command.decision.value,
            "expected_approval_fingerprint": command.expected_approval_fingerprint,
            "reviewer_comment": command.reviewer_comment or "",
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _calculate_decision_fingerprint(
        self,
        original_fingerprint: str,
        reviewer_id: str | uuid.UUID,
        tenant_id: str | uuid.UUID,
        approval_request_id: str | uuid.UUID,
        timestamp: datetime,
    ) -> str:
        """Calculate SHA-256 decision fingerprint over approval transition."""
        payload = {
            "original_approval_fingerprint": original_fingerprint,
            "reviewer_id": str(reviewer_id),
            "tenant_id": str(tenant_id),
            "approval_request_id": str(approval_request_id),
            "decision": ApprovalDecisionType.APPROVE.value,
            "timestamp": timestamp.isoformat(),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
