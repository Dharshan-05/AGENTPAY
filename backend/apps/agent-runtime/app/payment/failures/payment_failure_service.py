"""Payment Failure Handling Subsystem (Phase 296)."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from typing import Any

from app.payment.status.payment_status_service import PaymentStatusError, PaymentStatusService
from app.schemas.payment import PaymentStatus
from app.schemas.payment_failure import (
    PaymentFailureCategory,
    PaymentFailureCode,
    PaymentFailureRecord,
)

logger = logging.getLogger("agentpay.payment.failures")


class PaymentFailureError(Exception):
    """Domain exception raised when payment failure handling encounters unrecoverable errors."""


class PaymentFailureService:
    """Production Centralized Payment Failure Handling Service (Phase 296).

    Primary responsibility: Normalize provider errors, verification failures, authorization denials,
    and runtime exceptions into safe, deterministic, secret-free domain failure records.

    Integrates with PaymentStatusService to execute state transitions to FAILED without allowing
    failures to produce payment_success=True, payment_verified=True, or captured=True.
    """

    def __init__(self, status_service: PaymentStatusService | None = None) -> None:
        self.status_service = status_service or PaymentStatusService()

    def normalize_failure(
        self,
        err: Exception | Any,
        category: PaymentFailureCategory | None = None,
        failure_code: PaymentFailureCode | None = None,
        tenant_id: uuid.UUID | None = None,
        agent_id: uuid.UUID | None = None,
        transaction_id: str | None = None,
        order_id: str | None = None,
        payment_id: str | None = None,
        event_id: str | None = None,
        current_status: PaymentStatus | None = None,
    ) -> PaymentFailureRecord:
        """Normalize an error or exception into a safe PaymentFailureRecord (Phase 296).

        Redacts all sensitive credentials, authorization headers, or raw provider tokens.
        Executes state machine transition to PaymentStatus.FAILED via PaymentStatusService.
        """
        failure_id = uuid.uuid4()

        # 1. Infer Category & Failure Code if not explicitly provided
        resolved_category = category or self._infer_category(err)
        resolved_code = failure_code or self._infer_code(err, resolved_category)

        # 2. Sanitize Error Message (Zero Secrets)
        safe_msg = self.sanitize_message(str(err))

        # 3. Handle Payment Status State Machine Transition
        prev_status = current_status or PaymentStatus.PAYMENT_PENDING
        target_status = PaymentStatus.FAILED

        # Attempt state machine transition if current status permits
        new_status = prev_status
        if self.status_service.validate_transition(prev_status, target_status):
            try:
                res_tenant = tenant_id or uuid.uuid4()
                res_agent = agent_id or uuid.uuid4()
                res_tx = transaction_id or f"tx_fail_{failure_id.hex[:8]}"
                res_order = order_id or f"order_fail_{failure_id.hex[:8]}"

                rec = self.status_service.transition_status(
                    tenant_id=res_tenant,
                    agent_id=res_agent,
                    transaction_id=res_tx,
                    order_id=res_order,
                    previous_status=prev_status,
                    new_status=target_status,
                    transition_reason=f"FAILURE_{resolved_code.value}",
                    payment_id=payment_id,
                )
                new_status = rec.new_status
            except PaymentStatusError as status_err:
                logger.warning(
                    "Failure handling status transition prevented: %s", status_err.message
                )
                resolved_category = PaymentFailureCategory.STATE_TRANSITION_FAILURE
                resolved_code = PaymentFailureCode.PAYMENT_ILLEGAL_STATE_TRANSITION
                new_status = prev_status
        else:
            logger.info(
                "Transition %s -> FAILED is not permitted by state machine matrix.",
                prev_status.value,
            )
            resolved_category = PaymentFailureCategory.STATE_TRANSITION_FAILURE
            resolved_code = PaymentFailureCode.PAYMENT_ILLEGAL_STATE_TRANSITION
            new_status = prev_status

        # 4. Calculate Deterministic Failure Fingerprint (NO SECRETS)
        fingerprint = self.calculate_failure_fingerprint(
            failure_id=failure_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            event_id=event_id,
            category=resolved_category,
            failure_code=resolved_code,
            prev_status=prev_status,
            new_status=new_status,
        )

        logger.warning(
            "Payment failure normalized [category=%s, code=%s, tx=%s, fingerprint=%s...]",
            resolved_category.value,
            resolved_code.value,
            transaction_id,
            fingerprint[:12],
        )

        return PaymentFailureRecord(
            failure_id=failure_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            event_id=event_id,
            category=resolved_category,
            failure_code=resolved_code,
            safe_message=safe_msg,
            previous_status=prev_status,
            new_status=new_status,
            payment_success=False,
            payment_verified=False,
            captured=False,
            failure_fingerprint=fingerprint,
        )

    def sanitize_message(self, raw_msg: str) -> str:
        """Sanitize raw exception message to strip any credentials, secrets, or internal paths."""
        if not raw_msg or not raw_msg.strip():
            return "An unspecified payment error occurred."

        msg = raw_msg.strip()

        # Redact common secret patterns
        patterns = [
            (r"rzp_(live|test)_[A-Za-z0-9]+", "[REDACTED_KEY_ID]"),
            (
                r"(key_secret|webhook_secret|secret|password|bearer|authorization)=['\"]?[^'\";\s]+['\"]?",
                r"\1=[REDACTED]",
            ),
            (r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "Bearer [REDACTED]"),
            (r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+", "[REDACTED_JWT]"),
        ]

        for pat, repl in patterns:
            msg = re.sub(pat, repl, msg, flags=re.IGNORECASE)

        return msg

    def calculate_failure_fingerprint(
        self,
        failure_id: uuid.UUID,
        category: PaymentFailureCategory,
        failure_code: PaymentFailureCode,
        prev_status: PaymentStatus,
        new_status: PaymentStatus,
        tenant_id: uuid.UUID | None = None,
        agent_id: uuid.UUID | None = None,
        transaction_id: str | None = None,
        order_id: str | None = None,
        payment_id: str | None = None,
        event_id: str | None = None,
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe canonical failure metadata."""
        canonical = {
            "failure_id": str(failure_id),
            "tenant_id": str(tenant_id) if tenant_id else "",
            "agent_id": str(agent_id) if agent_id else "",
            "transaction_id": transaction_id or "",
            "order_id": order_id or "",
            "payment_id": payment_id or "",
            "event_id": event_id or "",
            "category": category.value,
            "failure_code": failure_code.value,
            "previous_status": prev_status.value,
            "new_status": new_status.value,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _infer_category(self, err: Exception | Any) -> PaymentFailureCategory:
        """Infer failure category from exception type or message."""
        name = type(err).__name__.lower()
        msg = str(err).lower()

        if "timeout" in name or "timeout" in msg:
            return PaymentFailureCategory.TIMEOUT
        if "authorization" in name or "authorization" in msg or "denied" in msg:
            return PaymentFailureCategory.AUTHORIZATION_FAILURE
        if "order" in msg or "order_creation" in name:
            return PaymentFailureCategory.ORDER_CREATION_FAILURE
        if "signature" in msg or "verification" in name or "verification" in msg:
            return PaymentFailureCategory.VERIFICATION_FAILURE
        if "provider" in name or "razorpay" in name or "provider" in msg:
            return PaymentFailureCategory.PROVIDER_FAILURE
        if "webhook" in name or "webhook" in msg:
            return PaymentFailureCategory.WEBHOOK_FAILURE
        if "transition" in msg or "state" in name:
            return PaymentFailureCategory.STATE_TRANSITION_FAILURE
        if "invalid" in msg or "valueerror" in name:
            return PaymentFailureCategory.INVALID_REQUEST

        return PaymentFailureCategory.UNKNOWN_FAILURE

    def _infer_code(
        self, err: Exception | Any, category: PaymentFailureCategory
    ) -> PaymentFailureCode:
        """Infer specific failure code from category and exception content."""
        msg = str(err).lower()

        if category == PaymentFailureCategory.TIMEOUT:
            return PaymentFailureCode.PAYMENT_TIMEOUT
        if category == PaymentFailureCategory.AUTHORIZATION_FAILURE:
            return PaymentFailureCode.PAYMENT_AUTHORIZATION_DENIED
        if category == PaymentFailureCategory.ORDER_CREATION_FAILURE:
            return PaymentFailureCode.PAYMENT_ORDER_CREATION_FAILED
        if category == PaymentFailureCategory.VERIFICATION_FAILURE:
            if "signature" in msg:
                return PaymentFailureCode.PAYMENT_SIGNATURE_INVALID
            if "amount" in msg:
                return PaymentFailureCode.PAYMENT_AMOUNT_MISMATCH
            if "currency" in msg:
                return PaymentFailureCode.PAYMENT_CURRENCY_MISMATCH
            return PaymentFailureCode.PAYMENT_VERIFICATION_FAILED
        if category == PaymentFailureCategory.PROVIDER_FAILURE:
            return PaymentFailureCode.PAYMENT_PROVIDER_UNAVAILABLE
        if category == PaymentFailureCategory.STATE_TRANSITION_FAILURE:
            return PaymentFailureCode.PAYMENT_ILLEGAL_STATE_TRANSITION

        return PaymentFailureCode.PAYMENT_UNKNOWN_FAILURE
