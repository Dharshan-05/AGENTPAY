"""Secure Agent-to-Razorpay Boundary Subsystem (Phase 300)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

from app.payment.authorization.payment_authorization_gate import PaymentAuthorizationGate
from app.payment.cancellation.payment_cancellation_service import PaymentCancellationService
from app.payment.failures.payment_failure_service import PaymentFailureService
from app.payment.payment_service import PaymentService
from app.payment.refunds.payment_refund_service import PaymentRefundService
from app.payment.status.payment_status_service import PaymentStatusService
from app.payment.verification.payment_verification import PaymentVerificationService
from app.schemas.agent_payment_boundary import (
    AgentPaymentCommand,
    AgentPaymentOperation,
    AgentPaymentResponse,
)
from app.schemas.payment import (
    PaymentServiceRequest,
    PaymentStatus,
    PaymentVerificationRequest,
    PaymentVerificationStatus,
)
from app.schemas.payment_cancellation import PaymentCancellationRequest
from app.schemas.payment_failure import PaymentFailureCategory, PaymentFailureCode
from app.schemas.payment_refund import PaymentRefundRequest
from app.schemas.risk_engine import FinalRiskDecisionResult

logger = logging.getLogger("agentpay.payment.boundary")


class AgentPaymentBoundaryError(Exception):
    """Domain exception raised when agent payment boundary validation fails."""

    def __init__(self, message: str, error_code: str = "BOUNDARY_SECURITY_VIOLATION") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AgentPaymentBoundary:
    """Production Secure Agent-to-Razorpay Boundary (Phase 300).

    Strengthens isolation between autonomous agents and Razorpay:
    - Agent is a REQUESTER ONLY, never a payment authority.
    - Zero agent access to key_secret, webhook_secret, credentials, or raw Razorpay SDK.
    - Agent cannot invoke RazorpayClientWrapper or RazorpayProvider directly.
    - Enforces strict operation allowlist (CREATE_ORDER, CHECKOUT, VERIFY, CANCEL, REFUND).
    - Prevents parameter tampering (amount, currency, provider, credentials).
    - Fails closed on missing or inconsistent identity/authorization context.
    """

    def __init__(
        self,
        authorization_gate: PaymentAuthorizationGate | None = None,
        payment_service: PaymentService | None = None,
        cancellation_service: PaymentCancellationService | None = None,
        refund_service: PaymentRefundService | None = None,
        verification_service: PaymentVerificationService | None = None,
        status_service: PaymentStatusService | None = None,
        failure_service: PaymentFailureService | None = None,
    ) -> None:
        self.authorization_gate = authorization_gate or PaymentAuthorizationGate()
        self.payment_service = payment_service or PaymentService(
            authorization_gate=self.authorization_gate
        )
        self.cancellation_service = cancellation_service or PaymentCancellationService()
        self.refund_service = refund_service or PaymentRefundService()
        self.verification_service = verification_service or PaymentVerificationService()
        self.status_service = status_service or PaymentStatusService()
        self.failure_service = failure_service or PaymentFailureService(
            status_service=self.status_service
        )

    def execute_agent_command(
        self,
        decision_result: FinalRiskDecisionResult,
        command: AgentPaymentCommand,
        current_status: PaymentStatus = PaymentStatus.ORDER_CREATED,
    ) -> AgentPaymentResponse:
        """Execute an agent payment command through server-side boundary (Phase 300)."""
        logger.info(
            "AgentPaymentBoundary executing operation '%s' for agent=%s, tx=%s (tenant=%s)",
            command.operation.value,
            command.agent_id,
            command.transaction_id,
            command.tenant_id,
        )

        # 1. Tenant / Agent / Transaction Identity Binding
        if decision_result.tenant_id != command.tenant_id:
            raise AgentPaymentBoundaryError(
                "Boundary Security Violation: Tenant identity mismatch!",
                error_code="TENANT_MISMATCH",
            )

        if decision_result.agent_id != command.agent_id:
            raise AgentPaymentBoundaryError(
                "Boundary Security Violation: Agent identity mismatch!",
                error_code="AGENT_MISMATCH",
            )

        if decision_result.transaction_id != command.transaction_id:
            raise AgentPaymentBoundaryError(
                "Boundary Security Violation: Transaction identity mismatch!",
                error_code="TRANSACTION_MISMATCH",
            )

        # 2. Authorization Fingerprint & Context Verification
        if not command.authorization_fingerprint or not command.authorization_id:
            raise AgentPaymentBoundaryError(
                "Boundary Security Violation: Missing authorization fingerprint!",
                error_code="AUTHORIZATION_FINGERPRINT_MISSING",
            )

        # 3. Dispatches Command safely via Allowlist
        try:
            if command.operation == AgentPaymentOperation.CREATE_ORDER:
                if command.amount is None or command.currency is None:
                    raise AgentPaymentBoundaryError(
                        "Amount and currency required for order creation.",
                        error_code="MISSING_ORDER_PARAMETERS",
                    )
                svc_req = PaymentServiceRequest(
                    tenant_id=command.tenant_id,
                    agent_id=command.agent_id,
                    transaction_id=command.transaction_id,
                    payment_reference=command.transaction_id,
                    amount=command.amount,
                    currency=command.currency,
                    idempotency_key=command.idempotency_key,
                )
                order_res = self.payment_service.create_payment_order(decision_result, svc_req)
                result_payload = order_res.model_dump(mode="json")
                status_str = "ORDER_CREATED"

            elif command.operation == AgentPaymentOperation.CHECKOUT:
                if command.order_id is None or command.amount is None or command.currency is None:
                    raise AgentPaymentBoundaryError(
                        "Order ID, amount, and currency required for checkout.",
                        error_code="MISSING_CHECKOUT_PARAMETERS",
                    )
                svc_req = PaymentServiceRequest(
                    tenant_id=command.tenant_id,
                    agent_id=command.agent_id,
                    transaction_id=command.transaction_id,
                    payment_reference=command.transaction_id,
                    amount=command.amount,
                    currency=command.currency,
                    idempotency_key=command.idempotency_key,
                )
                checkout_res = self.payment_service.generate_checkout_configuration(
                    decision_result=decision_result,
                    request=svc_req,
                )
                result_payload = checkout_res.model_dump(mode="json")
                status_str = "CHECKOUT_CONFIGURED"

            elif command.operation == AgentPaymentOperation.VERIFY:
                if (
                    command.order_id is None
                    or command.payment_id is None
                    or command.signature is None
                    or command.amount is None
                    or command.currency is None
                ):
                    raise AgentPaymentBoundaryError(
                        "Order ID, payment ID, signature, amount, currency required for verify.",
                        error_code="MISSING_VERIFICATION_PARAMETERS",
                    )
                verify_req = PaymentVerificationRequest(
                    tenant_id=command.tenant_id,
                    agent_id=command.agent_id,
                    transaction_id=command.transaction_id,
                    order_id=command.order_id,
                    payment_id=command.payment_id,
                    signature=command.signature,
                    amount=command.amount,
                    currency=command.currency,
                    authorization_id=command.authorization_id,
                    authorization_fingerprint=command.authorization_fingerprint,
                    idempotency_key=command.idempotency_key,
                )
                verify_res = self.verification_service.verify_payment(verify_req)
                result_payload = verify_res.model_dump(mode="json")
                status_str = (
                    "VERIFIED"
                    if verify_res.status == PaymentVerificationStatus.VERIFIED
                    else "VERIFICATION_FAILED"
                )

            elif command.operation == AgentPaymentOperation.CANCEL:
                if command.order_id is None:
                    raise AgentPaymentBoundaryError(
                        "Order ID required for cancellation.",
                        error_code="MISSING_CANCELLATION_PARAMETERS",
                    )
                cancel_req = PaymentCancellationRequest(
                    tenant_id=command.tenant_id,
                    agent_id=command.agent_id,
                    transaction_id=command.transaction_id,
                    order_id=command.order_id,
                    payment_id=command.payment_id,
                    authorization_id=command.authorization_id,
                    authorization_fingerprint=command.authorization_fingerprint,
                    idempotency_key=command.idempotency_key,
                    cancellation_reason=command.reason,
                )
                cancel_res = self.cancellation_service.cancel_payment(
                    decision_result=decision_result,
                    request=cancel_req,
                    current_status=current_status,
                )
                result_payload = cancel_res.model_dump(mode="json")
                status_str = "CANCELLED"

            elif command.operation == AgentPaymentOperation.REFUND:
                if (
                    command.order_id is None
                    or command.payment_id is None
                    or command.captured_amount is None
                    or command.refund_amount is None
                    or command.currency is None
                ):
                    raise AgentPaymentBoundaryError(
                        "Order ID, payment ID, captured amount, refund amount, "
                        "and currency required for refund.",
                        error_code="MISSING_REFUND_PARAMETERS",
                    )
                refund_req = PaymentRefundRequest(
                    tenant_id=command.tenant_id,
                    agent_id=command.agent_id,
                    transaction_id=command.transaction_id,
                    order_id=command.order_id,
                    payment_id=command.payment_id,
                    captured_amount=command.captured_amount,
                    refund_amount=command.refund_amount,
                    currency=command.currency,
                    authorization_id=command.authorization_id,
                    authorization_fingerprint=command.authorization_fingerprint,
                    idempotency_key=command.idempotency_key,
                    refund_reason=command.reason,
                )
                refund_res = self.refund_service.process_refund(
                    decision_result=decision_result,
                    request=refund_req,
                    current_status=current_status,
                )
                result_payload = refund_res.model_dump(mode="json")
                status_str = "REFUNDED"

            else:
                raise AgentPaymentBoundaryError(
                    f"Unsupported agent payment operation '{command.operation}'.",
                    error_code="UNSUPPORTED_OPERATION",
                )

            # 4. Compute Command Fingerprint
            command_id = uuid.uuid4()
            fingerprint = self.calculate_command_fingerprint(
                command_id=command_id,
                tenant_id=command.tenant_id,
                agent_id=command.agent_id,
                transaction_id=command.transaction_id,
                operation=command.operation,
                result_payload=result_payload,
            )

            return AgentPaymentResponse(
                command_id=command_id,
                tenant_id=command.tenant_id,
                agent_id=command.agent_id,
                transaction_id=command.transaction_id,
                operation=command.operation,
                status=status_str,
                command_fingerprint=fingerprint,
                result_payload=result_payload,
            )

        except Exception as err:
            self.failure_service.normalize_failure(
                err=err,
                category=PaymentFailureCategory.INVALID_REQUEST,
                failure_code=PaymentFailureCode.PAYMENT_UNKNOWN_FAILURE,
                tenant_id=command.tenant_id,
                agent_id=command.agent_id,
                transaction_id=command.transaction_id,
                order_id=command.order_id,
                payment_id=command.payment_id,
                current_status=current_status,
            )
            if not isinstance(err, AgentPaymentBoundaryError):
                raise AgentPaymentBoundaryError(f"Agent payment command failed: {err}") from err
            raise

    def calculate_command_fingerprint(
        self,
        command_id: uuid.UUID,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        operation: AgentPaymentOperation,
        result_payload: dict[str, Any],
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe command result payload."""
        canonical = {
            "command_id": str(command_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "operation": operation.value,
            "result_payload": result_payload,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
