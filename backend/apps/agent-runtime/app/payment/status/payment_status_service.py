"""Authoritative Payment Status State Machine Subsystem (Phase 292)."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from app.schemas.payment import (
    PaymentStatus,
    PaymentStatusTransitionRecord,
    PaymentVerificationResult,
    PaymentVerificationStatus,
)

logger = logging.getLogger("agentpay.payment.status")


class PaymentStatusError(Exception):
    """Domain exception raised when illegal payment status transitions occur (Phase 292)."""

    def __init__(
        self,
        message: str,
        reason_code: str = "ILLEGAL_STATUS_TRANSITION",
        previous_status: PaymentStatus | None = None,
        requested_status: PaymentStatus | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.reason_code = reason_code
        self.previous_status = previous_status
        self.requested_status = requested_status


class PaymentStatusService:
    """Authoritative Payment Lifecycle State Machine Service (Phase 292).

    Primary responsibility: Enforce an explicit state transition matrix preventing illegal state
    mutations, backward transitions, or client-driven forged status updates.

    FAILS CLOSED on any unauthorized or invalid state transition attempt.
    """

    # Explicit allowed state transitions map: source_status -> set of allowed target_statuses
    ALLOWED_TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
        PaymentStatus.CREATED: {
            PaymentStatus.ORDER_CREATED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        },
        PaymentStatus.ORDER_CREATED: {
            PaymentStatus.CHECKOUT_READY,
            PaymentStatus.PAYMENT_PENDING,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        },
        PaymentStatus.CHECKOUT_READY: {
            PaymentStatus.PAYMENT_PENDING,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        },
        PaymentStatus.PAYMENT_PENDING: {
            PaymentStatus.PAYMENT_RECEIVED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        },
        PaymentStatus.PAYMENT_RECEIVED: {
            PaymentStatus.PAYMENT_VERIFIED,
            PaymentStatus.FAILED,
        },
        PaymentStatus.PAYMENT_VERIFIED: {
            PaymentStatus.CAPTURED,
            PaymentStatus.FAILED,
        },
        PaymentStatus.CAPTURED: {
            PaymentStatus.REFUNDED,
        },
        # Terminal / Failure States
        PaymentStatus.FAILED: set(),
        PaymentStatus.CANCELLED: set(),
        PaymentStatus.REFUNDED: set(),
        PaymentStatus.UNKNOWN: set(),
    }

    def validate_transition(
        self,
        current_status: PaymentStatus,
        target_status: PaymentStatus,
    ) -> bool:
        """Return True if transition from current_status to target_status is valid."""
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    def transition_status(
        self,
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        order_id: str,
        previous_status: PaymentStatus,
        new_status: PaymentStatus,
        transition_reason: str,
        payment_id: str | None = None,
        verification_fingerprint: str | None = None,
    ) -> PaymentStatusTransitionRecord:
        """Perform an authoritative payment status transition.

        Validates current -> new transition against allowed transition matrix.
        Handles idempotency for same-state transition.
        Fails closed on illegal backward or terminal transitions.
        """
        logger.info(
            "Evaluating status transition for tx=%s: %s -> %s (reason: %s)",
            transaction_id,
            previous_status.value,
            new_status.value,
            transition_reason,
        )

        # 1. Idempotency Check: Same state transition is idempotent
        if previous_status == new_status:
            logger.info(
                "Status transition is IDEMPOTENT for tx=%s (%s)",
                transaction_id,
                new_status.value,
            )
            fingerprint = self.calculate_transition_fingerprint(
                tenant_id=tenant_id,
                agent_id=agent_id,
                transaction_id=transaction_id,
                order_id=order_id,
                payment_id=payment_id,
                prev_status=previous_status.value,
                new_status=new_status.value,
                reason="IDEMPOTENT_SAME_STATE",
            )
            return PaymentStatusTransitionRecord(
                tenant_id=tenant_id,
                agent_id=agent_id,
                transaction_id=transaction_id,
                order_id=order_id,
                payment_id=payment_id,
                previous_status=previous_status,
                new_status=new_status,
                transition_reason="IDEMPOTENT_SAME_STATE",
                verification_fingerprint=verification_fingerprint,
                transition_fingerprint=fingerprint,
            )

        # 2. Check Allowed Transition Matrix
        if not self.validate_transition(previous_status, new_status):
            msg = (
                f"Illegal payment status transition from {previous_status.value} "
                f"to {new_status.value} for transaction {transaction_id}."
            )
            logger.warning(msg)
            raise PaymentStatusError(
                message=msg,
                reason_code="ILLEGAL_STATUS_TRANSITION",
                previous_status=previous_status,
                requested_status=new_status,
            )

        # 3. Calculate Transition Fingerprint (NO SECRETS)
        fingerprint = self.calculate_transition_fingerprint(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            prev_status=previous_status.value,
            new_status=new_status.value,
            reason=transition_reason,
        )

        logger.info(
            "Status transition SUCCESS for tx=%s: %s -> %s",
            transaction_id,
            previous_status.value,
            new_status.value,
        )

        return PaymentStatusTransitionRecord(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            order_id=order_id,
            payment_id=payment_id,
            previous_status=previous_status,
            new_status=new_status,
            transition_reason=transition_reason,
            verification_fingerprint=verification_fingerprint,
            transition_fingerprint=fingerprint,
        )

    def transition_on_verification(
        self,
        verification_result: PaymentVerificationResult,
        current_status: PaymentStatus = PaymentStatus.PAYMENT_RECEIVED,
    ) -> PaymentStatusTransitionRecord:
        """Perform authoritative state transition driven by Phase 291 PaymentVerificationResult.

        If verification_result.status == VERIFIED -> transition to PAYMENT_VERIFIED.
        If verification_result.status != VERIFIED -> transition to FAILED.
        """
        if verification_result.status == PaymentVerificationStatus.VERIFIED:
            target_status = PaymentStatus.PAYMENT_VERIFIED
            reason = f"VERIFIED: {verification_result.reason_code}"
        else:
            target_status = PaymentStatus.FAILED
            reason = f"VERIFICATION_FAILED: {verification_result.reason_code}"

        # If current status is early (e.g. CHECKOUT_READY), bring through PAYMENT_RECEIVED first
        # if needed, or execute valid transition directly to target_status.
        effective_current = current_status
        if effective_current == PaymentStatus.CHECKOUT_READY:
            effective_current = PaymentStatus.PAYMENT_PENDING
        if effective_current == PaymentStatus.PAYMENT_PENDING:
            effective_current = PaymentStatus.PAYMENT_RECEIVED

        return self.transition_status(
            tenant_id=verification_result.tenant_id,
            agent_id=verification_result.agent_id,
            transaction_id=verification_result.transaction_id,
            order_id=verification_result.order_id,
            previous_status=effective_current,
            new_status=target_status,
            transition_reason=reason,
            payment_id=verification_result.payment_id,
            verification_fingerprint=verification_result.verification_fingerprint,
        )

    @staticmethod
    def calculate_transition_fingerprint(
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        order_id: str,
        payment_id: str | None,
        prev_status: str,
        new_status: str,
        reason: str,
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe canonical transition metadata.

        MUST NEVER contain key_secret, webhook_secret, or credentials.
        """
        canonical_str = (
            f"tenant:{tenant_id}|agent:{agent_id}|tx:{transaction_id}|"
            f"order:{order_id}|payment:{payment_id or 'none'}|"
            f"prev:{prev_status}|new:{new_status}|reason:{reason}"
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
