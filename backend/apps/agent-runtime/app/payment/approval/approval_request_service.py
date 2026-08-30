"""Approval Request Engine Subsystem (Phase 302)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.payment.approval.approval_audit_service import ApprovalAuditService
from app.schemas.approval_audit import ApprovalAuditActorType, ApprovalAuditEventType
from app.schemas.approval_request import (
    ApprovalRequestCreateResult,
    ApprovalRequestPriority,
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.payment_approval import ApprovalRequest, ApprovalStatus
from app.schemas.risk_engine import FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.approval.request")


class ApprovalRequestServiceError(Exception):
    """Domain exception raised when approval request creation/retrieval fails."""

    def __init__(self, message: str, error_code: str = "APPROVAL_REQUEST_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApprovalRequestConflictError(ApprovalRequestServiceError):
    """Exception raised when an idempotency key is reused with modified parameters (409)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="APPROVAL_REQUEST_CONFLICT")


class ApprovalRequestService:
    """Production Approval Request Engine Service (Phase 302).

    Primary responsibility: Create and manage immutable approval requests when ApprovalPolicyEngine
    evaluates approval_status = PENDING.

    Critical Invariants:
    - Binds tenant_id, agent_id, transaction_id, authorization_id, fingerprints.
    - All requests start as PENDING (cannot be created as APPROVED, REJECTED, EXPIRED, CANCELLED).
    - Prevents cross-tenant, cross-agent, or transaction tampering.
    - Multi-tenant thread-safe storage & idempotency handling.
    """

    def __init__(
        self,
        expiration_ttl_hours: int = 24,
        audit_service: ApprovalAuditService | None = None,
    ) -> None:
        self.expiration_ttl_hours = expiration_ttl_hours
        self.audit_service = audit_service or ApprovalAuditService()
        # In-memory thread-safe store keyed by request_id and idempotency identity
        self._store_by_id: dict[uuid.UUID, ApprovalRequestRecord] = {}
        self._store_by_idempotency: dict[str, tuple[ApprovalRequestRecord, str]] = {}
        self._lock = threading.Lock()

    def create_approval_request(
        self,
        decision_result: FinalRiskDecisionResult,
        approval_request: ApprovalRequest,
        idempotency_key: str,
        operation: str = "payment",
        expiration_ttl_hours: int | None = None,
    ) -> ApprovalRequestCreateResult:
        """Create or retrieve an authoritative approval request (Phase 302)."""
        logger.info(
            "ApprovalRequestService creating request for tx=%s (tenant=%s, agent=%s, amount=%s %s)",
            decision_result.transaction_id,
            decision_result.tenant_id,
            decision_result.agent_id,
            approval_request.amount,
            approval_request.currency.value,
        )

        # 1. Identity & Context Verification
        if decision_result.tenant_id != approval_request.tenant_id:
            raise ApprovalRequestServiceError(
                "Tenant identity mismatch between risk decision and approval request!",
                error_code="TENANT_MISMATCH",
            )

        if decision_result.agent_id != approval_request.agent_id:
            raise ApprovalRequestServiceError(
                "Agent identity mismatch between risk decision and approval request!",
                error_code="AGENT_MISMATCH",
            )

        if decision_result.transaction_id != approval_request.transaction_id:
            raise ApprovalRequestServiceError(
                "Transaction identity mismatch between risk decision and approval request!",
                error_code="TRANSACTION_MISMATCH",
            )

        # 2. Status Guard: Must be PENDING
        if approval_request.approval_status != ApprovalStatus.PENDING:
            raise ApprovalRequestServiceError(
                f"Cannot create request for status '{approval_request.approval_status.value}'. "
                "Approval request creation requires status PENDING.",
                error_code="INVALID_INITIAL_STATUS",
            )

        # 3. Derive Priority based on Risk Score & Amount
        priority = self._derive_priority(
            risk_score=decision_result.composite_risk_score,
            amount=approval_request.amount,
        )

        # 4. Idempotency Key Computation & Thread-Safe Check
        idemp_identity = (
            f"{decision_result.tenant_id}|{decision_result.agent_id}|"
            f"{decision_result.transaction_id}|{idempotency_key}"
        )
        param_fp = self._calculate_params_fingerprint(
            amount=approval_request.amount,
            currency=approval_request.currency,
            operation=operation,
        )

        ttl_hours = expiration_ttl_hours or self.expiration_ttl_hours
        now_utc = datetime.now(UTC)
        expires_at = now_utc + timedelta(hours=ttl_hours)

        with self._lock:
            if idemp_identity in self._store_by_idempotency:
                existing_record, stored_fp = self._store_by_idempotency[idemp_identity]
                if stored_fp != param_fp:
                    raise ApprovalRequestConflictError(
                        "Idempotency key reused with modified financial parameters!"
                    )
                creation_fp = self._calculate_creation_fingerprint(existing_record)
                return ApprovalRequestCreateResult(
                    request_record=existing_record,
                    is_existing=True,
                    creation_fingerprint=creation_fp,
                )

            # Construct new immutable record
            record = ApprovalRequestRecord(
                approval_request_id=approval_request.approval_id,
                tenant_id=decision_result.tenant_id,
                agent_id=decision_result.agent_id,
                transaction_id=decision_result.transaction_id,
                order_id=approval_request.order_id,
                payment_id=approval_request.payment_id,
                authorization_id=uuid.uuid4(),  # Authoritative authorization ref
                authorization_fingerprint=decision_result.decision_fingerprint,
                approval_fingerprint=approval_request.approval_fingerprint,
                amount=approval_request.amount,
                currency=approval_request.currency,
                operation=operation,
                policy_version="1.0.0",
                status=ApprovalRequestStatus.PENDING,
                risk_score=decision_result.composite_risk_score,
                priority=priority,
                idempotency_key=idempotency_key,
                created_at=now_utc,
                expires_at=expires_at,
            )

            self._store_by_id[record.approval_request_id] = record
            self._store_by_idempotency[idemp_identity] = (record, param_fp)

            creation_fp = self._calculate_creation_fingerprint(record)

            # Record Audit Event (Phase 308)
            self.audit_service.record_event(
                tenant_id=record.tenant_id,
                approval_request_id=record.approval_request_id,
                transaction_id=record.transaction_id,
                agent_id=record.agent_id,
                event_type=ApprovalAuditEventType.APPROVAL_REQUEST_CREATED,
                actor_type=ApprovalAuditActorType.SYSTEM,
                resulting_status=ApprovalRequestStatus.PENDING,
                authorization_id=record.authorization_id,
                authorization_fingerprint=record.authorization_fingerprint,
                approval_fingerprint=record.approval_fingerprint,
                metadata={"priority": record.priority.value},
            )

        logger.info(
            "Approval request CREATED successfully for tx=%s (request_id=%s, priority=%s)",
            record.transaction_id,
            record.approval_request_id,
            record.priority.value,
        )

        return ApprovalRequestCreateResult(
            request_record=record,
            is_existing=False,
            creation_fingerprint=creation_fp,
        )

    def get_approval_request(
        self, tenant_id: uuid.UUID, approval_request_id: uuid.UUID
    ) -> ApprovalRequestRecord | None:
        """Retrieve an approval request record by ID enforcing tenant isolation."""
        with self._lock:
            record = self._store_by_id.get(approval_request_id)
            if record is None:
                return None
            if record.tenant_id != tenant_id:
                # Anti-enumeration cross-tenant isolation
                return None
            return record

    def list_all_requests_internal(self) -> list[ApprovalRequestRecord]:
        """Internal helper returning all records for queue integration."""
        with self._lock:
            return list(self._store_by_id.values())

    def _derive_priority(self, risk_score: float, amount: Decimal) -> ApprovalRequestPriority:
        """Derive priority deterministically based on risk score and monetary value."""
        if risk_score >= 80.0 or amount >= Decimal("100000.00"):
            return ApprovalRequestPriority.CRITICAL
        if risk_score >= 50.0 or amount >= Decimal("50000.00"):
            return ApprovalRequestPriority.HIGH
        if risk_score >= 30.0 or amount >= Decimal("10000.00"):
            return ApprovalRequestPriority.MEDIUM
        return ApprovalRequestPriority.LOW

    def _calculate_params_fingerprint(
        self, amount: Decimal, currency: SupportedCurrency, operation: str
    ) -> str:
        """Calculate fingerprint over mutable parameter payload for idempotency checking."""
        payload = {
            "amount": str(amount),
            "currency": currency.value,
            "operation": operation,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _calculate_creation_fingerprint(self, record: ApprovalRequestRecord) -> str:
        """Calculate SHA-256 fingerprint over creation event."""
        payload = {
            "approval_request_id": str(record.approval_request_id),
            "tenant_id": str(record.tenant_id),
            "agent_id": str(record.agent_id),
            "transaction_id": record.transaction_id,
            "amount": str(record.amount),
            "currency": record.currency.value,
            "operation": record.operation,
            "status": record.status.value,
            "idempotency_key": record.idempotency_key,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
