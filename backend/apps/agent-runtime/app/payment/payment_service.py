"""Payment Application Service Boundary (Phase 288)."""

from __future__ import annotations

import logging
from typing import Any

from app.payment.authorization.payment_authorization_gate import PaymentAuthorizationGate
from app.payment.idempotency.payment_idempotency_service import PaymentIdempotencyService
from app.payment.providers.base import PaymentProvider
from app.payment.providers.razorpay.credentials import RazorpayCredentialResolver
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import (
    PaymentOrderRequest,
    PaymentOrderResult,
    PaymentServiceOutcome,
    PaymentServiceRequest,
    PaymentServiceResult,
    RazorpayCheckoutConfig,
)
from app.schemas.payment_authorization import (
    PaymentAuthorizationOutcome,
    PaymentAuthorizationRequest,
)
from app.schemas.risk_engine import FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.service")


class PaymentServiceError(Exception):
    """Base domain exception for PaymentService errors. Never leaks secrets."""


class PaymentOperationOutOfScopeError(PaymentServiceError):
    """Exception raised when an operation belonging to future phases (289+) is invoked."""


class PaymentService:
    """Production Payment Service Boundary (Phase 288–297).

    Coordinates payment authorization gate enforcement, credential validation,
    payment order creation, and Phase 297 payment idempotency enforcement.
    """

    def __init__(
        self,
        authorization_gate: PaymentAuthorizationGate | None = None,
        provider: PaymentProvider | None = None,
        credential_resolver: RazorpayCredentialResolver | None = None,
        idempotency_service: PaymentIdempotencyService | None = None,
    ) -> None:
        self.authorization_gate = authorization_gate or PaymentAuthorizationGate()
        self.provider = provider or RazorpayProvider()
        self.credential_resolver = credential_resolver or RazorpayCredentialResolver()
        self.idempotency_service = idempotency_service or PaymentIdempotencyService()

    def evaluate_payment_request(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentServiceRequest,
        max_decision_age_seconds: float = 300.0,
    ) -> PaymentServiceResult:
        """Evaluate payment request against decision and authorization gate (Phase 288)."""
        logger.info(
            "Evaluating payment service request for tx=%s (tenant=%s, agent=%s, amount=%s %s)",
            request.transaction_id,
            request.tenant_id,
            request.agent_id,
            request.amount,
            request.currency,
        )

        # 1. Identity Binding Defense-in-Depth
        if decision_result.tenant_id != request.tenant_id:
            logger.error("PaymentService failed: tenant mismatch!")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code="IDENTITY_TENANT_MISMATCH",
                decision_result=decision_result,
            )

        if decision_result.agent_id != request.agent_id:
            logger.error("PaymentService failed: agent mismatch!")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code="IDENTITY_AGENT_MISMATCH",
                decision_result=decision_result,
            )

        if decision_result.transaction_id != request.transaction_id:
            logger.error("PaymentService failed: transaction mismatch!")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code="IDENTITY_TRANSACTION_MISMATCH",
                decision_result=decision_result,
            )

        # 2. Enforce Payment Authorization Gate
        auth_ts = (
            request.evaluated_at if hasattr(request, "evaluated_at") else decision_result.created_at
        )
        auth_request = PaymentAuthorizationRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            payment_reference=request.payment_reference,
            authorization_timestamp=auth_ts,
            context_metadata=request.context_metadata,
        )
        auth_res = self.authorization_gate.authorize_payment(
            decision_result=decision_result,
            request=auth_request,
            max_decision_age_seconds=max_decision_age_seconds,
        )

        if auth_res.outcome == PaymentAuthorizationOutcome.DENIED:
            logger.warning("Payment authorization gate DENIED execution.")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code=f"AUTHORIZATION_GATE_DENIED_{auth_res.reason_code}",
                decision_result=decision_result,
                authorization_id=auth_res.authorization_id,
                auth_fingerprint=auth_res.authorization_fingerprint,
            )

        if auth_res.outcome == PaymentAuthorizationOutcome.SUSPENDED:
            logger.warning("Payment authorization gate SUSPENDED execution for human approval.")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.SUSPENDED_FOR_APPROVAL,
                reason_code=f"AUTHORIZATION_GATE_SUSPENDED_{auth_res.reason_code}",
                decision_result=decision_result,
                authorization_id=auth_res.authorization_id,
                auth_fingerprint=auth_res.authorization_fingerprint,
            )

        # 3. Verify Payment Provider Support & Credentials
        if request.provider_name.lower() != self.provider.provider_name.lower():
            logger.error("Unsupported payment provider '%s'", request.provider_name)
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code="UNSUPPORTED_PAYMENT_PROVIDER",
                decision_result=decision_result,
                authorization_id=auth_res.authorization_id,
                auth_fingerprint=auth_res.authorization_fingerprint,
            )

        if not self.provider.validate_configuration():
            logger.error("Payment provider configuration invalid or disabled.")
            return self._build_result(
                request,
                outcome=PaymentServiceOutcome.DENIED,
                reason_code="PROVIDER_CREDENTIALS_INVALID",
                decision_result=decision_result,
                authorization_id=auth_res.authorization_id,
                auth_fingerprint=auth_res.authorization_fingerprint,
            )

        # 4. Return Phase 288 AUTHORIZED_FOR_PAYMENT Outcome (Order Creation belongs to Phase 289)
        return self._build_result(
            request,
            outcome=PaymentServiceOutcome.AUTHORIZED_FOR_PAYMENT,
            reason_code="PAYMENT_AUTHORIZED_READY_FOR_PHASE_289_EXECUTION",
            decision_result=decision_result,
            authorization_id=auth_res.authorization_id,
            auth_fingerprint=auth_res.authorization_fingerprint,
        )

    def create_payment_order(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentServiceRequest,
        max_decision_age_seconds: float = 300.0,
    ) -> PaymentOrderResult:
        """Create a real Razorpay Order downstream of authorization (Phase 289).

        MUST be downstream of:
        FinalRiskDecisionResult -> PaymentAuthorizationGate -> PaymentService -> RazorpayProvider.
        REVIEW and BLOCK decisions MUST NEVER create an order.
        """
        logger.info(
            "Attempting payment order creation for tx=%s (tenant=%s, agent=%s, amount=%s %s)",
            request.transaction_id,
            request.tenant_id,
            request.agent_id,
            request.amount,
            request.currency,
        )

        # 0. Phase 297 Payment Idempotency Reservation BEFORE financial side effects
        from app.schemas.payment_idempotency import IdempotencyState

        req_params = {
            "amount": str(request.amount),
            "currency": request.currency,
            "provider": request.provider_name,
        }
        fp = self.idempotency_service.compute_request_fingerprint(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="create_payment_order",
            request_params=req_params,
        )

        idemp_rec, is_new = self.idempotency_service.reserve_idempotency(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            operation="create_payment_order",
            idempotency_key=request.idempotency_key,
            request_fingerprint=fp,
        )

        if not is_new:
            if idemp_rec.state == IdempotencyState.COMPLETED and idemp_rec.safe_result_payload:
                logger.info(
                    "Replaying previous PaymentOrderResult from idempotency store for tx=%s",
                    request.transaction_id,
                )
                return PaymentOrderResult.model_validate(idemp_rec.safe_result_payload)

            if idemp_rec.state == IdempotencyState.IN_PROGRESS:
                msg = f"Payment order creation in progress for tx {request.transaction_id}."
                logger.warning(msg)
                raise PaymentServiceError(msg)

            if idemp_rec.state == IdempotencyState.FAILED:
                msg = (
                    f"Previous payment order creation failed for tx {request.transaction_id} "
                    f"({idemp_rec.error_code})."
                )
                logger.warning(msg)
                raise PaymentServiceError(msg)

        try:
            # 1. Identity Binding Defense-in-Depth
            if decision_result.tenant_id != request.tenant_id:
                raise PaymentServiceError("Payment order creation failed: tenant mismatch!")

            if decision_result.agent_id != request.agent_id:
                raise PaymentServiceError("Payment order creation failed: agent mismatch!")

            if decision_result.transaction_id != request.transaction_id:
                raise PaymentServiceError("Payment order creation failed: transaction mismatch!")

            # 2. Enforce Payment Authorization Gate
            auth_ts = (
                request.evaluated_at
                if hasattr(request, "evaluated_at")
                else decision_result.created_at
            )
            auth_request = PaymentAuthorizationRequest(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                payment_reference=request.payment_reference,
                authorization_timestamp=auth_ts,
                context_metadata=request.context_metadata,
            )
            auth_res = self.authorization_gate.authorize_payment(
                decision_result=decision_result,
                request=auth_request,
                max_decision_age_seconds=max_decision_age_seconds,
            )

            if auth_res.outcome == PaymentAuthorizationOutcome.DENIED:
                logger.warning("Order creation blocked: Payment authorization gate DENIED.")
                raise PaymentServiceError(
                    f"Payment order creation DENIED by authorization gate: {auth_res.reason_code}"
                )

            if auth_res.outcome == PaymentAuthorizationOutcome.SUSPENDED:
                logger.warning("Order creation blocked: Payment authorization gate SUSPENDED.")
                raise PaymentServiceError(
                    f"Payment order creation SUSPENDED for human approval: {auth_res.reason_code}"
                )

            if auth_res.outcome != PaymentAuthorizationOutcome.PERMITTED:
                raise PaymentServiceError(
                    f"Payment order creation blocked: Invalid gate outcome '{auth_res.outcome}'."
                )

            # 3. Verify Payment Provider Support & Credentials
            if request.provider_name.lower() != self.provider.provider_name.lower():
                raise PaymentServiceError(
                    f"Unsupported payment provider '{request.provider_name}'."
                )

            if not self.provider.validate_configuration():
                raise PaymentServiceError(
                    "Payment provider credentials invalid or provider disabled."
                )

            # 4. Construct Provider Order Request
            order_req = PaymentOrderRequest(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                amount=request.amount,
                currency=request.currency,
                idempotency_key=request.idempotency_key,
                receipt=request.payment_reference or f"rcpt_{request.transaction_id}",
                notes={"provider": request.provider_name},
            )

            # 5. Create Order via Provider
            from typing import cast

            order_res = cast(
                PaymentOrderResult,
                self.provider.create_order(
                    request=order_req,
                    auth_id=auth_res.authorization_id,
                    auth_fp=auth_res.authorization_fingerprint,
                ),
            )

            # Complete idempotency record
            self.idempotency_service.complete_idempotency(
                record_id=idemp_rec.record_id,
                safe_result_payload=order_res.model_dump(mode="json"),
            )

            return order_res

        except Exception as err:
            self.idempotency_service.fail_idempotency(
                record_id=idemp_rec.record_id,
                error_code=type(err).__name__,
            )
            if not isinstance(err, PaymentServiceError):
                raise PaymentServiceError(f"Payment order creation failed: {err}") from err
            raise

    def generate_checkout_configuration(
        self,
        decision_result: FinalRiskDecisionResult,
        request: PaymentServiceRequest,
        order_result: PaymentOrderResult | None = None,
        max_decision_age_seconds: float = 300.0,
    ) -> RazorpayCheckoutConfig:
        """Generate safe frontend-facing Razorpay Checkout configuration (Phase 290).

        Exposes public key_id to the browser, keeping key_secret strictly server-side.
        Binds configuration to the server-created Razorpay order and authorization gate result.
        """
        logger.info(
            "Generating Razorpay checkout configuration for tx=%s (tenant=%s, agent=%s)",
            request.transaction_id,
            request.tenant_id,
            request.agent_id,
        )

        # If order_result is provided, verify order identity binding
        if order_result is not None:
            if order_result.tenant_id != request.tenant_id:
                raise PaymentServiceError("Checkout generation failed: Order tenant mismatch!")
            if order_result.agent_id != request.agent_id:
                raise PaymentServiceError("Checkout generation failed: Order agent mismatch!")
            if order_result.transaction_id != request.transaction_id:
                raise PaymentServiceError("Checkout generation failed: Order transaction mismatch!")
            target_order = order_result
        else:
            # Create order downstream of authorization
            target_order = self.create_payment_order(
                decision_result=decision_result,
                request=request,
                max_decision_age_seconds=max_decision_age_seconds,
            )

        # Resolve credentials safely to get public key_id
        creds = self.credential_resolver.get_credentials(tenant_id=request.tenant_id)
        if not creds.key_id:
            raise PaymentServiceError("Razorpay key_id is missing or unconfigured.")

        from app.schemas.payment import RazorpayCheckoutConfig, amount_to_minor_units

        amount_minor = amount_to_minor_units(request.amount, request.currency)

        return RazorpayCheckoutConfig(
            key_id=creds.key_id,
            order_id=target_order.order_id,
            amount=request.amount,
            amount_minor_units=amount_minor,
            currency=request.currency,
            name="AGENTPAY",
            description=f"Payment authorization for tx {request.transaction_id}",
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            checkout_status="CHECKOUT_READY",
            payment_success=False,
            payment_verified=False,
        )

    def _build_result(
        self,
        request: PaymentServiceRequest,
        outcome: PaymentServiceOutcome,
        reason_code: str,
        decision_result: FinalRiskDecisionResult | None = None,
        authorization_id: Any = None,
        auth_fingerprint: str | None = None,
    ) -> PaymentServiceResult:
        return PaymentServiceResult(
            authorization_id=authorization_id,
            decision_id=decision_result.decision_id if decision_result else None,
            evaluation_id=decision_result.evaluation_id if decision_result else None,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            amount=request.amount,
            currency=request.currency,
            idempotency_key=request.idempotency_key,
            outcome=outcome,
            reason_code=reason_code,
            decision_reason=decision_result.decision_reason if decision_result else None,
            provider_name=request.provider_name,
            authorization_fingerprint=auth_fingerprint,
            payment_id=None,
            order_id=None,
        )
