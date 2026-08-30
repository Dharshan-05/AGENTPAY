"""Intent Verification Application Service for AGENTPAY (Phase 197)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.intent_verification import (
    IntentVerificationRequest,
    IntentVerificationResult,
)

logger = logging.getLogger("agentguard.security.intent_verification")


class IntentVerificationService:
    """Production Intent Verification Engine (Phase 197 - Read/Decision Subsystem Only)."""

    ACTION_ALIASES = {
        "pay": "PAYMENT",
        "payment": "PAYMENT",
        "purchase": "PAYMENT",
        "buy": "PAYMENT",
        "checkout": "PAYMENT",
        "refund": "REFUND",
        "cancel": "CANCEL",
    }

    def _normalize_action(self, action: str | None) -> str:
        if not action or not action.strip():
            return "UNKNOWN"
        raw = action.strip().lower()
        return self.ACTION_ALIASES.get(raw, raw.upper())

    def verify_intent(
        self,
        request: IntentVerificationRequest,
    ) -> IntentVerificationResult:
        """Verify declared intent against requested commercial action fail-closed (Phase 197)."""
        now = datetime.now(UTC)

        # 1. Missing declared intent check (Fail-closed)
        if not request.declared_intent:
            return IntentVerificationResult(
                verified=False,
                decision="INSUFFICIENT",
                reason_code="INTENT_MISSING",
                confidence_score=Decimal("0.00"),
                explanation="No declared intent specification was provided for verification.",
                evaluated_at=now,
            )

        intent = request.declared_intent

        # 2. Action Normalization & Comparison
        norm_declared_action = self._normalize_action(intent.action)
        norm_requested_action = self._normalize_action(request.requested_action)

        if norm_declared_action != norm_requested_action:
            return IntentVerificationResult(
                verified=False,
                decision="MISMATCH",
                reason_code="ACTION_MISMATCH",
                confidence_score=Decimal("0.00"),
                explanation=f"Action mismatch: declared '{intent.action}' ({norm_declared_action}) != requested '{request.requested_action}' ({norm_requested_action}).",  # noqa: E501
                evaluated_at=now,
            )

        # 3. Currency Match Validation
        if intent.currency and request.requested_currency:
            if intent.currency.strip().upper() != request.requested_currency.strip().upper():
                return IntentVerificationResult(
                    verified=False,
                    decision="MISMATCH",
                    reason_code="CURRENCY_MISMATCH",
                    confidence_score=Decimal("0.00"),
                    explanation=f"Currency mismatch: declared '{intent.currency}' != requested '{request.requested_currency}'.",  # noqa: E501
                    evaluated_at=now,
                )

        # 4. Amount Boundary Validation (Decimal precision)
        if intent.amount is not None and request.requested_amount is not None:
            if request.requested_amount > intent.amount:
                return IntentVerificationResult(
                    verified=False,
                    decision="MISMATCH",
                    reason_code="AMOUNT_MISMATCH",
                    confidence_score=Decimal("0.00"),
                    explanation=f"Amount mismatch: requested amount ({request.requested_amount}) exceeds declared max intent ({intent.amount}).",  # noqa: E501
                    evaluated_at=now,
                )

        # 5. Merchant Identity Validation
        if intent.merchant_id and request.requested_merchant_id:
            if intent.merchant_id != request.requested_merchant_id:
                return IntentVerificationResult(
                    verified=False,
                    decision="MISMATCH",
                    reason_code="MERCHANT_MISMATCH",
                    confidence_score=Decimal("0.00"),
                    explanation=f"Merchant mismatch: declared '{intent.merchant_id}' != requested '{request.requested_merchant_id}'.",  # noqa: E501
                    evaluated_at=now,
                )

        # 6. Intent Verified
        return IntentVerificationResult(
            verified=True,
            decision="VERIFIED",
            reason_code="INTENT_VERIFIED",
            confidence_score=Decimal("1.00"),
            explanation="Declared intent matches requested commercial operation.",
            evaluated_at=now,
        )
