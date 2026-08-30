"""Payment Cancellation Subsystem (Phase 298)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid

from app.payment.failures.payment_failure_service import (
    PaymentFailureService,
)
from app.payment.idempotency.payment_idempotency_service import (
    PaymentIdempotencyConflictError,
    PaymentIdempotencyService,
)
from app.payment.providers.base import PaymentProvider
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.payment.status.payment_status_service import PaymentStatusService
from app.schemas.payment import PaymentStatus
from app.schemas.payment_cancellation import (
    PaymentCancellationRequest,
    PaymentCancellationResult,
)
from app.schemas.payment_failure import PaymentFailureCategory, PaymentFailureCode
from app.schemas.payment_idempotency import IdempotencyState
from app.schemas.risk_engine import FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.cancellation")


class PaymentCancellationError(Exception):
    """Domain exception raised when payment cancellation fails."""

    def __init__(self, message: str, error_code: str = "CANCELLATION_FAILED") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class PaymentCancellationEligibilityError(PaymentCancellationError):
    """Exception raised when payment status is ineligible for cancellation."""

    def __init__(self, current_status: PaymentStatus) -> None:
        super().__init__(
            message=f"Payment status '{current_status.value}' is ineligible for cancellation.",
            error_code="INELIGIBLE_FOR_CANCELLATION",
        )


class PaymentCancellationService:
    """Production Payment Cancellation Service Boundary (Phase 298).

    Primary responsibility: Execute server-side payment order cancellation.
    - Allowed Policy: CREATED, ORDER_CREATED, CHECKOUT_READY, PAYMENT_PENDING -> CANCELLED.
    - Rejected Policy: PAYMENT_RECEIVED, PAYMENT_VERIFIED, CAPTURED, REFUNDED, FAILED, CANCELLED.
    - Strictly forbids CAPTURED -> CANCELLED (cancellation is NOT refund).
    - Enforces idempotency via PaymentIdempotencyService.
    - Integrates with PaymentStatusService for state machine transition.
    """

    ALLOWED_CANCELLATION_STATES = {
        PaymentStatus.CREATED,
        PaymentStatus.ORDER_CREATED,
        PaymentStatus.CHECKOUT_READY,
        PaymentStatus.PAYMENT_PENDING,
    }

    REJECTED_CANCELLATION_STATES = {
        PaymentStatus.PAYMENT_RECEIVED,
        PaymentStatus.PAYMENT_VERIFIED,
        PaymentStatus.CAPTURED,
        PaymentStatus.REFUNDED,
        PaymentStatus.FAILED,
        PaymentStatus.CANCELLED,
    }

    def __init__(
        self,
        status_service: PaymentStatusService | None = None,
        provider: PaymentProvider | None = None,
        idempotency_service: PaymentIdempotencyService | None = None,
        failure_service: PaymentFailureService | None = None,
    ) -> None:
        self.status_service = status_service or PaymentStatusService()
        self.provider = provider or RazorpayProvider()
        self.idempotency_service = idempotency_service or PaymentIdempotencyService()
        self.failure_service = failure_service or PaymentFailureService(
            status_service=self.status_service
        )

    def cancel_payment(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentCancellationRequest,
        current_status: PaymentStatus,
    ) -> PaymentCancellationResult:
        """Cancel a payment order (Phase 298)."""
        logger.info(
            "Attempting payment cancellation for order=%s, tx=%s (tenant=%s, agent=%s)",
            request.order_id,
            request.transaction_id,
            request.tenant_id,
            request.agent_id,
        )

        # 1. Identity & Context Validation
        if decision_result.tenant_id != request.tenant_id:
            raise PaymentCancellationError(
                "Cancellation failed: Tenant identity mismatch!", error_code="TENANT_MISMATCH"
            )

        if decision_result.agent_id != request.agent_id:
            raise PaymentCancellationError(
                "Cancellation failed: Agent identity mismatch!", error_code="AGENT_MISMATCH"
            )

        if decision_result.transaction_id != request.transaction_id:
            raise PaymentCancellationError(
                "Cancellation failed: Transaction identity mismatch!",
                error_code="TRANSACTION_MISMATCH",
            )

        # 2. Authorization Fingerprint Verification
        if not request.authorization_fingerprint or not request.authorization_id:
            raise PaymentCancellationError(
                "Cancellation failed: Missing authorization fingerprint!",
                error_code="AUTHORIZATION_FINGERPRINT_MISSING",
            )

        # 3. Cancellation Eligibility Check
        if current_status in self.REJECTED_CANCELLATION_STATES:
            logger.warning(
                "Cancellation rejected: Status '%s' is in REJECTED_CANCELLATION_STATES",
                current_status.value,
            )
            raise PaymentCancellationEligibilityError(current_status=current_status)

        if current_status not in self.ALLOWED_CANCELLATION_STATES:
            logger.warning(
                "Cancellation rejected: Status '%s' is not in ALLOWED_CANCELLATION_STATES",
                current_status.value,
            )
            raise PaymentCancellationEligibilityError(current_status=current_status)

        # 4. Phase 297 Idempotency Reservation
        req_params = {
            "order_id": request.order_id,
            "payment_id": request.payment_id or "",
            "provider": self.provider.provider_name,
        }
        fp = self.idempotency_service.compute_request_fingerprint(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="payment_cancellation",
            request_params=req_params,
        )

        idemp_rec, is_new = self.idempotency_service.reserve_idempotency(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="payment_cancellation",
            idempotency_key=request.idempotency_key,
            request_fingerprint=fp,
        )

        if not is_new:
            if idemp_rec.state == IdempotencyState.COMPLETED and idemp_rec.safe_result_payload:
                logger.info(
                    "Replaying previous PaymentCancellationResult from idempotency store "
                    "for order=%s",
                    request.order_id,
                )
                return PaymentCancellationResult.model_validate(idemp_rec.safe_result_payload)

            if idemp_rec.state == IdempotencyState.IN_PROGRESS:
                raise PaymentCancellationError(
                    f"Payment cancellation in progress for tx {request.transaction_id}.",
                    error_code="CANCELLATION_IN_PROGRESS",
                )

            if idemp_rec.state == IdempotencyState.FAILED:
                raise PaymentCancellationError(
                    f"Previous payment cancellation failed ({idemp_rec.error_code}).",
                    error_code="PREVIOUS_CANCELLATION_FAILED",
                )

        try:
            # 5. Provider Cancellation Call
            self.provider.cancel_payment(
                order_id=request.order_id,
                payment_id=request.payment_id,
                tenant_id=request.tenant_id,
                reason=request.cancellation_reason,
            )

            # 6. Authoritative PaymentStatus State Transition
            self.status_service.transition_status(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                previous_status=current_status,
                new_status=PaymentStatus.CANCELLED,
                transition_reason=request.cancellation_reason or "CLIENT_CANCELLATION_REQUESTED",
                payment_id=request.payment_id,
            )

            # 7. Compute Cancellation Fingerprint
            cancellation_id = uuid.uuid4()
            fingerprint = self.calculate_cancellation_fingerprint(
                cancellation_id=cancellation_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                prev_status=current_status,
                new_status=PaymentStatus.CANCELLED,
            )

            result = PaymentCancellationResult(
                cancellation_id=cancellation_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                cancellation_status=PaymentStatus.CANCELLED,
                previous_status=current_status,
                provider_name=self.provider.provider_name,
                cancellation_reason=request.cancellation_reason,
                cancellation_fingerprint=fingerprint,
            )

            # 8. Complete Idempotency Store
            self.idempotency_service.complete_idempotency(
                record_id=idemp_rec.record_id,
                safe_result_payload=result.model_dump(mode="json"),
            )

            logger.info("Payment order %s CANCELLED successfully.", request.order_id)
            return result

        except PaymentIdempotencyConflictError:
            raise

        except Exception as err:
            self.idempotency_service.fail_idempotency(
                record_id=idemp_rec.record_id,
                error_code=type(err).__name__,
            )
            # Flow failure through PaymentFailureService
            self.failure_service.normalize_failure(
                err=err,
                category=PaymentFailureCategory.ORDER_CREATION_FAILURE,
                failure_code=PaymentFailureCode.PAYMENT_ORDER_CREATION_FAILED,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                current_status=current_status,
            )
            if not isinstance(err, PaymentCancellationError):
                raise PaymentCancellationError(f"Payment cancellation failed: {err}") from err
            raise

    def calculate_cancellation_fingerprint(
        self,
        cancellation_id: uuid.UUID,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        order_id: str,
        prev_status: PaymentStatus,
        new_status: PaymentStatus,
        payment_id: str | None = None,
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe cancellation metadata."""
        canonical = {
            "cancellation_id": str(cancellation_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "order_id": order_id,
            "payment_id": payment_id or "",
            "previous_status": prev_status.value,
            "new_status": new_status.value,
            "provider": self.provider.provider_name,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
