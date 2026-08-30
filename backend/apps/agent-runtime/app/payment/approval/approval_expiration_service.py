"""Production Approval Expiration Subsystem (Phase 307)."""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import UTC, datetime, timedelta

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.schemas.approval_audit import ApprovalAuditActorType, ApprovalAuditEventType
from app.schemas.approval_expiration import ApprovalExpirationResult
from app.schemas.approval_request import ApprovalRequestStatus

logger = logging.getLogger("agentpay.payment.approval.expiration")


class ApprovalExpirationError(Exception):
    """Domain exception raised when an approval expiration operation fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_EXPIRATION_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalExpirationService:
    """Production Approval Expiration Service (Phase 307).

    Primary responsibility: Evaluate and execute state transition PENDING -> EXPIRED
    for payment approval requests whose server-authoritative deadline has passed.

    CRITICAL SECURITY & EXECUTION BOUNDARIES:
    - State Machine: Strict transition PENDING -> EXPIRED.
    - Server-authoritative UTC time evaluation (now_utc >= expires_at).
    - Cannot overwrite existing terminal states (APPROVED, REJECTED, CANCELLED).
    - Idempotent and thread-safe evaluation.
    - MUST NOT call Razorpay SDK or execute payment operations.
    - MUST NOT mutate payment status service.
    - MUST NOT perform destructive record deletion.
    """

    def __init__(
        self,
        request_service: ApprovalRequestService | None = None,
        audit_service: ApprovalAuditService | None = None,
        default_ttl_hours: int = 24,
    ) -> None:
        self.request_service = request_service or ApprovalRequestService()
        self.audit_service = audit_service or ApprovalAuditService()
        self.default_ttl_hours = default_ttl_hours
        self._lock = threading.Lock()

    def expire_approval_request(
        self,
        approval_request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        now_utc: datetime | None = None,
    ) -> ApprovalExpirationResult:
        """Evaluate and expire a single approval request if overdue (Phase 307)."""
        eval_time = now_utc or datetime.now(UTC)
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=UTC)

        logger.info(
            "ApprovalExpirationService evaluating req=%s (tenant=%s, now=%s)",
            approval_request_id,
            tenant_id,
            eval_time.isoformat(),
        )

        with self._lock:
            approval_request = self.request_service.get_approval_request(
                tenant_id=tenant_id,
                approval_request_id=approval_request_id,
            )

            if approval_request is None:
                raise ApprovalExpirationError(
                    f"Approval request '{approval_request_id}' not found.",
                    error_code="APPROVAL_REQUEST_NOT_FOUND",
                )

            # 1. Idempotency Check: Already EXPIRED
            if approval_request.status == ApprovalRequestStatus.EXPIRED:
                return ApprovalExpirationResult(
                    approval_request_id=approval_request_id,
                    tenant_id=tenant_id,
                    previous_status=ApprovalRequestStatus.EXPIRED,
                    resulting_status=ApprovalRequestStatus.EXPIRED,
                    expired_at=eval_time,
                    is_expired=True,
                    is_existing=True,
                    reason_code="ALREADY_EXPIRED",
                )

            # 2. Terminal State Guard: APPROVED, REJECTED, CANCELLED cannot be expired!
            if approval_request.status in (
                ApprovalRequestStatus.APPROVED,
                ApprovalRequestStatus.REJECTED,
                ApprovalRequestStatus.CANCELLED,
            ):
                return ApprovalExpirationResult(
                    approval_request_id=approval_request_id,
                    tenant_id=tenant_id,
                    previous_status=approval_request.status,
                    resulting_status=approval_request.status,
                    expired_at=eval_time,
                    is_expired=False,
                    is_existing=False,
                    reason_code="TERMINAL_STATE_CANNOT_EXPIRE",
                )

            # 3. PENDING Deadline Evaluation
            expires_at = approval_request.created_at + timedelta(hours=self.default_ttl_hours)

            if eval_time >= expires_at:
                # Transition status PENDING -> EXPIRED
                updated_record = approval_request.model_copy(
                    update={"status": ApprovalRequestStatus.EXPIRED}
                )
                self.request_service._store_by_id[approval_request_id] = updated_record

                # Record Audit Event (Phase 308)
                self.audit_service.record_event(
                    tenant_id=approval_request.tenant_id,
                    approval_request_id=approval_request.approval_request_id,
                    transaction_id=approval_request.transaction_id,
                    agent_id=approval_request.agent_id,
                    event_type=ApprovalAuditEventType.APPROVAL_EXPIRED,
                    actor_type=ApprovalAuditActorType.SYSTEM,
                    previous_status=ApprovalRequestStatus.PENDING,
                    resulting_status=ApprovalRequestStatus.EXPIRED,
                    approval_fingerprint=approval_request.approval_fingerprint,
                    metadata={"expires_at": expires_at.isoformat()},
                )

                logger.info(
                    "Approval request EXPIRED successfully (req_id=%s, expires_at=%s)",
                    approval_request_id,
                    expires_at.isoformat(),
                )

                return ApprovalExpirationResult(
                    approval_request_id=approval_request_id,
                    tenant_id=tenant_id,
                    previous_status=ApprovalRequestStatus.PENDING,
                    resulting_status=ApprovalRequestStatus.EXPIRED,
                    expired_at=eval_time,
                    is_expired=True,
                    is_existing=False,
                    reason_code="APPROVAL_EXPIRED",
                )

            # Not yet expired
            return ApprovalExpirationResult(
                approval_request_id=approval_request_id,
                tenant_id=tenant_id,
                previous_status=ApprovalRequestStatus.PENDING,
                resulting_status=ApprovalRequestStatus.PENDING,
                expired_at=eval_time,
                is_expired=False,
                is_existing=False,
                reason_code="APPROVAL_NOT_YET_EXPIRED",
            )

    def expire_eligible_requests(
        self,
        tenant_id: uuid.UUID | None = None,
        now_utc: datetime | None = None,
    ) -> list[ApprovalExpirationResult]:
        """Scan pending requests and expire any overdue requests (Phase 307)."""
        eval_time = now_utc or datetime.now(UTC)
        results: list[ApprovalExpirationResult] = []

        all_requests = self.request_service.list_all_requests_internal()

        for req in all_requests:
            if tenant_id is not None and req.tenant_id != tenant_id:
                continue
            if req.status == ApprovalRequestStatus.PENDING:
                res = self.expire_approval_request(
                    approval_request_id=req.approval_request_id,
                    tenant_id=req.tenant_id,
                    now_utc=eval_time,
                )
                if res.is_expired:
                    results.append(res)

        return results
