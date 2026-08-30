"""Payment Refund Subsystem (Phase 299)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from decimal import Decimal

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
from app.schemas.payment import PaymentStatus, SupportedCurrency, amount_to_minor_units
from app.schemas.payment_failure import PaymentFailureCategory, PaymentFailureCode
from app.schemas.payment_idempotency import IdempotencyState
from app.schemas.payment_refund import PaymentRefundRequest, PaymentRefundResult
from app.schemas.risk_engine import FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.refunds")


class PaymentRefundError(Exception):
    """Domain exception raised when payment refund processing fails."""

    def __init__(self, message: str, error_code: str = "REFUND_FAILED") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class PaymentRefundEligibilityError(PaymentRefundError):
    """Exception raised when payment status is ineligible for refund."""

    def __init__(self, current_status: PaymentStatus) -> None:
        super().__init__(
            message=(
                f"Payment status '{current_status.value}' is ineligible for refund. "
                "Only CAPTURED payments can be refunded."
            ),
            error_code="INELIGIBLE_FOR_REFUND",
        )


class PaymentRefundAmountError(PaymentRefundError):
    """Exception raised when refund monetary amount validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, error_code="INVALID_REFUND_AMOUNT")


class PaymentRefundService:
    """Production Payment Refund Service Boundary (Phase 299).

    Primary responsibility: Execute server-side payment refund processing.
    - Allowed Policy: CAPTURED -> REFUNDED ONLY.
    - Rejected Policy: CREATED, ORDER_CREATED, CHECKOUT_READY, PAYMENT_PENDING,
      PAYMENT_RECEIVED, PAYMENT_VERIFIED, FAILED, CANCELLED, REFUNDED.
    - Enforces Decimal monetary precision (refund_amount > 0, refund_amount <= captured_amount).
    - Enforces idempotency via PaymentIdempotencyService.
    - Integrates with PaymentStatusService for state machine transition.
    """

    ALLOWED_REFUND_STATES = {PaymentStatus.CAPTURED}

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

    def process_refund(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentRefundRequest,
        current_status: PaymentStatus = PaymentStatus.CAPTURED,
    ) -> PaymentRefundResult:
        """Process payment refund for a captured payment (Phase 299)."""
        logger.info(
            "Attempting payment refund for pay=%s, order=%s, tx=%s (amount=%s %s)",
            request.payment_id,
            request.order_id,
            request.transaction_id,
            request.refund_amount,
            request.currency,
        )

        # 1. Identity & Context Validation
        if decision_result.tenant_id != request.tenant_id:
            raise PaymentRefundError(
                "Refund failed: Tenant identity mismatch!", error_code="TENANT_MISMATCH"
            )

        if decision_result.agent_id != request.agent_id:
            raise PaymentRefundError(
                "Refund failed: Agent identity mismatch!", error_code="AGENT_MISMATCH"
            )

        if decision_result.transaction_id != request.transaction_id:
            raise PaymentRefundError(
                "Refund failed: Transaction identity mismatch!", error_code="TRANSACTION_MISMATCH"
            )

        # 2. Authorization Fingerprint Verification
        if not request.authorization_fingerprint or not request.authorization_id:
            raise PaymentRefundError(
                "Refund failed: Missing authorization fingerprint!",
                error_code="AUTHORIZATION_FINGERPRINT_MISSING",
            )

        # 3. Refund Eligibility Check (CAPTURED ONLY)
        if current_status not in self.ALLOWED_REFUND_STATES:
            logger.warning("Refund rejected: Status '%s' is not CAPTURED.", current_status.value)
            raise PaymentRefundEligibilityError(current_status=current_status)

        # 4. Monetary Amount Validation
        if request.refund_amount > request.captured_amount:
            raise PaymentRefundAmountError(
                f"Refund amount ({request.refund_amount}) cannot exceed "
                f"captured amount ({request.captured_amount})."
            )

        # 5. Phase 297 Idempotency Reservation
        req_params = {
            "payment_id": request.payment_id,
            "order_id": request.order_id,
            "refund_amount": str(request.refund_amount),
            "currency": request.currency.value,
            "provider": self.provider.provider_name,
        }
        fp = self.idempotency_service.compute_request_fingerprint(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="payment_refund",
            request_params=req_params,
        )

        idemp_rec, is_new = self.idempotency_service.reserve_idempotency(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="payment_refund",
            idempotency_key=request.idempotency_key,
            request_fingerprint=fp,
        )

        if not is_new:
            if idemp_rec.state == IdempotencyState.COMPLETED and idemp_rec.safe_result_payload:
                logger.info(
                    "Replaying previous PaymentRefundResult from idempotency store for pay=%s",
                    request.payment_id,
                )
                return PaymentRefundResult.model_validate(idemp_rec.safe_result_payload)

            if idemp_rec.state == IdempotencyState.IN_PROGRESS:
                raise PaymentRefundError(
                    f"Payment refund in progress for tx {request.transaction_id}.",
                    error_code="REFUND_IN_PROGRESS",
                )

            if idemp_rec.state == IdempotencyState.FAILED:
                raise PaymentRefundError(
                    f"Previous payment refund failed ({idemp_rec.error_code}).",
                    error_code="PREVIOUS_REFUND_FAILED",
                )

        try:
            # 6. Provider Refund Execution
            amount_minor = amount_to_minor_units(request.refund_amount, request.currency)
            provider_res = self.provider.refund_payment(
                payment_id=request.payment_id,
                amount_minor=amount_minor,
                currency=request.currency.value,
                order_id=request.order_id,
                tenant_id=request.tenant_id,
                notes={
                    "reason": request.refund_reason or "CLIENT_REFUND_REQUESTED",
                    "transaction_id": request.transaction_id,
                },
            )

            if isinstance(provider_res, dict) and isinstance(provider_res.get("id"), str):
                provider_refund_id = str(provider_res["id"])
            else:
                provider_refund_id = f"rfnd_rzp_mock_{uuid.uuid4().hex[:12]}"

            # 7. Authoritative PaymentStatus State Transition (CAPTURED -> REFUNDED)
            self.status_service.transition_status(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                previous_status=current_status,
                new_status=PaymentStatus.REFUNDED,
                transition_reason=request.refund_reason or "CLIENT_REFUND_EXECUTED",
                payment_id=request.payment_id,
            )

            # 8. Compute Refund Fingerprint
            refund_id = uuid.uuid4()
            fingerprint = self.calculate_refund_fingerprint(
                refund_id=refund_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                provider_refund_id=provider_refund_id,
                refund_amount=request.refund_amount,
                currency=request.currency,
            )

            result = PaymentRefundResult(
                refund_id=refund_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                provider_refund_id=provider_refund_id,
                refund_amount=request.refund_amount,
                captured_amount=request.captured_amount,
                currency=request.currency,
                refund_status=PaymentStatus.REFUNDED,
                previous_status=current_status,
                provider_name=self.provider.provider_name,
                refund_reason=request.refund_reason,
                refund_fingerprint=fingerprint,
            )

            # 9. Complete Idempotency Store
            self.idempotency_service.complete_idempotency(
                record_id=idemp_rec.record_id,
                safe_result_payload=result.model_dump(mode="json"),
            )

            logger.info("Payment %s REFUNDED successfully.", request.payment_id)
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
                category=PaymentFailureCategory.PROVIDER_FAILURE,
                failure_code=PaymentFailureCode.PAYMENT_PROVIDER_UNAVAILABLE,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                order_id=request.order_id,
                payment_id=request.payment_id,
                current_status=current_status,
            )
            if not isinstance(err, PaymentRefundError):
                raise PaymentRefundError(f"Payment refund failed: {err}") from err
            raise

    def calculate_refund_fingerprint(
        self,
        refund_id: uuid.UUID,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        order_id: str,
        payment_id: str,
        provider_refund_id: str,
        refund_amount: Decimal,
        currency: SupportedCurrency,
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe refund metadata."""
        canonical = {
            "refund_id": str(refund_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "order_id": order_id,
            "payment_id": payment_id,
            "provider_refund_id": provider_refund_id,
            "refund_amount": str(refund_amount),
            "currency": currency.value,
            "previous_status": PaymentStatus.CAPTURED.value,
            "new_status": PaymentStatus.REFUNDED.value,
            "provider": self.provider.provider_name,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
