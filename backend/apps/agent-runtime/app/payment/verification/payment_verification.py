"""Production Payment Verification Service Boundary (Phase 291)."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from app.payment.providers.base import PaymentProvider
from app.payment.providers.razorpay.credentials import RazorpayCredentialResolver
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import (
    PaymentOrderResult,
    PaymentVerificationRequest,
    PaymentVerificationResult,
    PaymentVerificationStatus,
)

logger = logging.getLogger("agentpay.payment.verification")


class PaymentVerificationError(Exception):
    """Domain exception raised when payment verification fails closed (Phase 291)."""

    def __init__(
        self,
        message: str,
        reason_code: str = "PAYMENT_VERIFICATION_FAILED",
        status: PaymentVerificationStatus = PaymentVerificationStatus.FAILED,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.reason_code = reason_code
        self.status = status


class PaymentVerificationService:
    """Production-grade Payment Verification Subsystem (Phase 291).

    Primary responsibility: Synchronously verify that a payment reported by the client/provider
    corresponds to the server-created Razorpay order, authorized transaction, correct amount,
    and valid cryptographic HMAC-SHA256 signature.

    FAILS CLOSED on any identity mismatch, amount tampering, or invalid signature.
    """

    def __init__(
        self,
        provider: PaymentProvider | None = None,
        credential_resolver: RazorpayCredentialResolver | None = None,
    ) -> None:
        self.provider = provider or RazorpayProvider()
        self.credential_resolver = credential_resolver or RazorpayCredentialResolver()

    def verify_payment(
        self,
        request: PaymentVerificationRequest,
        order_result: PaymentOrderResult | None = None,
    ) -> PaymentVerificationResult:
        """Verify client-reported payment payload against authoritative server order context.

        MUST NOT trust client-claimed payment success.
        Independently performs:
        1. Contextual identity & order binding verification
        2. Amount & currency integrity verification
        3. Authorization fingerprint verification
        4. Cryptographic HMAC-SHA256 signature verification via RazorpayProvider

        Fails closed on any failure.
        """
        logger.info(
            "Executing payment verification for tx=%s (order=%s, payment=%s, tenant=%s)",
            request.transaction_id,
            request.order_id,
            request.payment_id,
            request.tenant_id,
        )

        # 1. Server Order Context Integrity Check
        if order_result is not None:
            if request.tenant_id != order_result.tenant_id:
                logger.warning(
                    "Payment verification tenant mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.IDENTITY_MISMATCH,
                    reason_code="TENANT_IDENTITY_MISMATCH",
                )

            if request.agent_id != order_result.agent_id:
                logger.warning(
                    "Payment verification agent mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.IDENTITY_MISMATCH,
                    reason_code="AGENT_IDENTITY_MISMATCH",
                )

            if request.transaction_id != order_result.transaction_id:
                logger.warning(
                    "Payment verification transaction mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.IDENTITY_MISMATCH,
                    reason_code="TRANSACTION_IDENTITY_MISMATCH",
                )

            if request.order_id != order_result.order_id:
                logger.warning(
                    "Payment verification order_id mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.INVALID_ORDER,
                    reason_code="ORDER_ID_MISMATCH",
                )

            if request.amount != order_result.amount:
                logger.warning(
                    "Payment verification amount mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.AMOUNT_MISMATCH,
                    reason_code="AMOUNT_INTEGRITY_MISMATCH",
                )

            if request.currency != order_result.currency:
                logger.warning(
                    "Payment verification currency mismatch for tx=%s", request.transaction_id
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.CURRENCY_MISMATCH,
                    reason_code="CURRENCY_INTEGRITY_MISMATCH",
                )

            if request.authorization_id != order_result.authorization_id:
                logger.warning(
                    "Payment verification authorization_id mismatch for tx=%s",
                    request.transaction_id,
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.IDENTITY_MISMATCH,
                    reason_code="AUTHORIZATION_ID_MISMATCH",
                )

            if request.authorization_fingerprint != order_result.authorization_fingerprint:
                logger.warning(
                    "Payment verification authorization fingerprint mismatch for tx=%s",
                    request.transaction_id,
                )
                return self._build_failed_result(
                    request,
                    status=PaymentVerificationStatus.IDENTITY_MISMATCH,
                    reason_code="AUTHORIZATION_FINGERPRINT_MISMATCH",
                )

        # 2. Input Integrity Checks
        if not request.payment_id or not request.payment_id.strip():
            return self._build_failed_result(
                request,
                status=PaymentVerificationStatus.INVALID_PAYMENT,
                reason_code="MISSING_PAYMENT_ID",
            )

        if not request.signature or not request.signature.strip():
            return self._build_failed_result(
                request,
                status=PaymentVerificationStatus.INVALID_SIGNATURE,
                reason_code="MISSING_SIGNATURE",
            )

        # 3. Provider Check
        if not self.provider.is_enabled:
            return self._build_failed_result(
                request,
                status=PaymentVerificationStatus.UNAVAILABLE,
                reason_code="PROVIDER_DISABLED",
            )

        # 4. Cryptographic HMAC-SHA256 Signature Verification via Provider
        sig_valid = self.provider.verify_payment_signature(
            order_id=request.order_id,
            payment_id=request.payment_id,
            signature=request.signature,
            tenant_id=request.tenant_id,
        )

        if not sig_valid:
            logger.warning(
                "Payment verification signature validation failed for tx=%s", request.transaction_id
            )
            return self._build_failed_result(
                request,
                status=PaymentVerificationStatus.INVALID_SIGNATURE,
                reason_code="HMAC_SIGNATURE_INVALID",
            )

        # 5. Deterministic Verification Fingerprint Calculation (NO SECRETS)
        fingerprint = self.calculate_verification_fingerprint(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            order_id=request.order_id,
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency.value,
            auth_id=request.authorization_id,
            auth_fp=request.authorization_fingerprint,
        )

        logger.info(
            "Payment verification PASSED for tx=%s (order=%s, payment=%s)",
            request.transaction_id,
            request.order_id,
            request.payment_id,
        )

        return PaymentVerificationResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            order_id=request.order_id,
            payment_id=request.payment_id,
            status=PaymentVerificationStatus.VERIFIED,
            reason_code="PAYMENT_VERIFIED_SUCCESSFULLY",
            amount=request.amount,
            currency=request.currency,
            payment_success=True,
            payment_verified=True,
            captured=False,  # Phase 291 synchronous verification is NOT payment capture
            verification_fingerprint=fingerprint,
        )

    def _build_failed_result(
        self,
        request: PaymentVerificationRequest,
        status: PaymentVerificationStatus,
        reason_code: str,
    ) -> PaymentVerificationResult:
        """Helper to construct a safe failed verification result."""
        fingerprint = self.calculate_verification_fingerprint(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            order_id=request.order_id,
            payment_id=request.payment_id,
            amount=request.amount,
            currency=request.currency.value,
            auth_id=request.authorization_id,
            auth_fp=request.authorization_fingerprint,
            status=status.value,
        )
        return PaymentVerificationResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            order_id=request.order_id,
            payment_id=request.payment_id,
            status=status,
            reason_code=reason_code,
            amount=request.amount,
            currency=request.currency,
            payment_success=False,
            payment_verified=False,
            captured=False,
            verification_fingerprint=fingerprint,
        )

    @staticmethod
    def calculate_verification_fingerprint(
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        order_id: str,
        payment_id: str,
        amount: Any,
        currency: str,
        auth_id: Any,
        auth_fp: str,
        status: str = "VERIFIED",
    ) -> str:
        """Calculate deterministic SHA-256 fingerprint over safe canonical verification metadata.

        MUST NEVER contain key_secret, webhook_secret, or credentials.
        """
        canonical_str = (
            f"tenant:{tenant_id}|agent:{agent_id}|tx:{transaction_id}|"
            f"order:{order_id}|payment:{payment_id}|amount:{amount}|"
            f"currency:{currency}|auth:{auth_id}|auth_fp:{auth_fp}|status:{status}"
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
