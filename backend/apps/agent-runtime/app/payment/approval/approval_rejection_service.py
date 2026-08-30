"""Production Approval Rejection Subsystem (Phase 306)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from datetime import UTC, datetime

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.reviewer_authorization_service import (
    ReviewerAuthorizationService,
)
from app.schemas.approval_audit import ApprovalAuditActorType, ApprovalAuditEventType
from app.schemas.approval_rejection import (
    ApprovalRejectionCommand,
    ApprovalRejectionResult,
)
from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.reviewer_authorization import ReviewerPermission

logger = logging.getLogger("agentpay.payment.approval.rejection")


class ApprovalRejectionError(Exception):
    """Domain exception raised when approval rejection fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_REJECTION_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalRejectionConflictError(ApprovalRejectionError):
    """Raised when an idempotency key is reused with modified parameters (409)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="REJECTION_IDEMPOTENCY_CONFLICT")


class ApprovalRejectionService:
    """Production Approval Rejection Service (Phase 306).

    Primary responsibility: Execute state transition PENDING -> REJECTED for payment approval
    requests when ALL reviewer authorization controls succeed.

    CRITICAL SECURITY & EXECUTION BOUNDARIES:
    - State Machine: Strict transition PENDING -> REJECTED.
    - Idempotency & TOCTOU protection under thread-safe lock.
    - Integrates with ReviewerAuthorizationService (Phase 304).
    - MUST NOT call Razorpay SDK, create payment orders, or execute payment logic.
    - MUST NOT mutate payment status service.
    - MUST NOT recalculate risk scores.
    """

    def __init__(
        self,
        request_service: ApprovalRequestService | None = None,
        auth_service: ReviewerAuthorizationService | None = None,
        audit_service: ApprovalAuditService | None = None,
    ) -> None:
        self.request_service = request_service or ApprovalRequestService()
        self.auth_service = auth_service or ReviewerAuthorizationService()
        self.audit_service = audit_service or ApprovalAuditService()
        self._lock = threading.Lock()
        # In-memory store for rejection idempotency: key -> (Result, params_fingerprint)
        self._idempotency_store: dict[str, tuple[ApprovalRejectionResult, str]] = {}

    def reject_request(self, command: ApprovalRejectionCommand) -> ApprovalRejectionResult:
        """Execute state transition PENDING -> REJECTED for an approval request (Phase 306)."""
        logger.info(
            "ApprovalRejectionService processing rejection for req=%s (tenant=%s, reviewer=%s)",
            command.approval_request_id,
            command.tenant_id,
            command.reviewer_context.reviewer_id,
        )

        with self._lock:
            # 1. Calculate Request Fingerprint for Idempotency Check
            params_fp = self._calculate_params_fingerprint(command)
            idemp_key = f"{command.tenant_id}:{command.idempotency_key}"

            # 2. Check Idempotency Store
            if idemp_key in self._idempotency_store:
                existing_res, existing_fp = self._idempotency_store[idemp_key]
                if existing_fp != params_fp:
                    raise ApprovalRejectionConflictError(
                        f"Idempotency key '{command.idempotency_key}' was previously used with "
                        "different rejection parameters."
                    )
                return ApprovalRejectionResult(
                    approval_request_id=existing_res.approval_request_id,
                    tenant_id=existing_res.tenant_id,
                    transaction_id=existing_res.transaction_id,
                    reviewer_id=existing_res.reviewer_id,
                    previous_status=existing_res.previous_status,
                    resulting_status=existing_res.resulting_status,
                    rejection_reason=existing_res.rejection_reason,
                    decision_fingerprint=existing_res.decision_fingerprint,
                    processed_at=existing_res.processed_at,
                    is_existing=True,
                )

            # 3. Lookup Authoritative Approval Request
            approval_request = self.request_service.get_approval_request(
                tenant_id=command.tenant_id,
                approval_request_id=command.approval_request_id,
            )

            if approval_request is None:
                raise ApprovalRejectionError(
                    f"Approval request '{command.approval_request_id}' not found.",
                    error_code="APPROVAL_REQUEST_NOT_FOUND",
                )

            # 4. State Machine Transition Guard: Must be PENDING
            if approval_request.status == ApprovalRequestStatus.REJECTED:
                raise ApprovalRejectionError(
                    f"Approval request '{command.approval_request_id}' is ALREADY_REJECTED.",
                    error_code="ALREADY_REJECTED",
                )

            if approval_request.status != ApprovalRequestStatus.PENDING:
                raise ApprovalRejectionError(
                    f"Cannot transition status '{approval_request.status.value}' to REJECTED.",
                    error_code="INVALID_STATE_TRANSITION",
                )

            # 5. Evaluate Reviewer Authorization (Phase 304 Integration)
            auth_res = self.auth_service.authorize_reviewer(
                reviewer_context=command.reviewer_context,
                approval_request=approval_request,
                required_permission=ReviewerPermission.REJECT_PAYMENT,
                expected_approval_fingerprint=command.expected_approval_fingerprint,
            )

            if not auth_res.authorized:
                raise ApprovalRejectionError(
                    f"Reviewer authorization DENIED: {auth_res.reason_code}",
                    error_code=auth_res.reason_code,
                )

            # 6. Atomic TOCTOU State Mutation under Lock
            now_utc = datetime.now(UTC)
            updated_record = approval_request.model_copy(
                update={"status": ApprovalRequestStatus.REJECTED}
            )
            # Update request in service internal store
            self.request_service._store_by_id[updated_record.approval_request_id] = updated_record

            # 7. Compute Decision Fingerprint
            dec_fp = self._calculate_decision_fingerprint(
                original_fingerprint=approval_request.approval_fingerprint,
                reviewer_id=command.reviewer_context.reviewer_id,
                tenant_id=command.tenant_id,
                approval_request_id=command.approval_request_id,
                rejection_reason=command.rejection_reason.value,
                timestamp=now_utc,
            )

            result = ApprovalRejectionResult(
                approval_request_id=command.approval_request_id,
                tenant_id=command.tenant_id,
                transaction_id=approval_request.transaction_id,
                reviewer_id=command.reviewer_context.reviewer_id,
                previous_status=ApprovalRequestStatus.PENDING,
                resulting_status=ApprovalRequestStatus.REJECTED,
                rejection_reason=command.rejection_reason,
                decision_fingerprint=dec_fp,
                processed_at=now_utc,
                is_existing=False,
            )

            # Save in idempotency map
            self._idempotency_store[idemp_key] = (result, params_fp)

            # Record Audit Event (Phase 308)
            self.audit_service.record_event(
                tenant_id=approval_request.tenant_id,
                approval_request_id=approval_request.approval_request_id,
                transaction_id=approval_request.transaction_id,
                agent_id=approval_request.agent_id,
                event_type=ApprovalAuditEventType.APPROVAL_REJECTED,
                actor_type=ApprovalAuditActorType.REVIEWER,
                actor_id=command.reviewer_context.reviewer_id,
                previous_status=ApprovalRequestStatus.PENDING,
                resulting_status=ApprovalRequestStatus.REJECTED,
                approval_fingerprint=approval_request.approval_fingerprint,
                metadata={
                    "rejection_reason": command.rejection_reason.value,
                    "decision_fingerprint": dec_fp,
                },
            )

            logger.info(
                "Approval request REJECTED successfully (req_id=%s, dec_fp=%s)",
                command.approval_request_id,
                dec_fp,
            )

            return result

    def _calculate_params_fingerprint(self, command: ApprovalRejectionCommand) -> str:
        """Calculate SHA-256 fingerprint over rejection command parameters."""
        payload = {
            "approval_request_id": str(command.approval_request_id),
            "tenant_id": str(command.tenant_id),
            "reviewer_id": str(command.reviewer_context.reviewer_id),
            "rejection_reason": command.rejection_reason.value,
            "reviewer_comment": command.reviewer_comment or "",
            "expected_approval_fingerprint": command.expected_approval_fingerprint,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _calculate_decision_fingerprint(
        self,
        original_fingerprint: str,
        reviewer_id: str | uuid.UUID,
        tenant_id: str | uuid.UUID,
        approval_request_id: str | uuid.UUID,
        rejection_reason: str,
        timestamp: datetime,
    ) -> str:
        """Compute SHA-256 fingerprint over canonical rejection decision data."""
        payload = {
            "original_approval_fingerprint": original_fingerprint,
            "reviewer_id": str(reviewer_id),
            "tenant_id": str(tenant_id),
            "approval_request_id": str(approval_request_id),
            "decision": "REJECT",
            "rejection_reason": rejection_reason,
            "decided_at": timestamp.isoformat(),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
