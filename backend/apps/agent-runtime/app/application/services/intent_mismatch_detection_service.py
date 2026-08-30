"""Intent Mismatch Detection Application Service for AGENTPAY (Phase 199)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.schemas.intent_mismatch import (
    IntentMismatchDetectionRequest,
    IntentMismatchDetectionResult,
)

logger = logging.getLogger("agentguard.security.intent_mismatch_detection")


class IntentMismatchDetectionService:
    """Production Intent Mismatch Detection Engine (Phase 199 - Read/Decision Only)."""

    SEVERITY_RANK = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "NONE": 0,
    }

    SIGNAL_SEVERITY_MAP = {
        "amount": ("AMOUNT_MISMATCH", "CRITICAL"),
        "currency": ("CURRENCY_MISMATCH", "CRITICAL"),
        "merchant": ("MERCHANT_MISMATCH", "CRITICAL"),
        "action": ("ACTION_MISMATCH", "HIGH"),
        "category": ("CATEGORY_MISMATCH", "MEDIUM"),
        "product": ("PRODUCT_MISMATCH", "HIGH"),
        "quantity": ("QUANTITY_MISMATCH", "MEDIUM"),
    }

    def detect_mismatches(
        self,
        request: IntentMismatchDetectionRequest,
    ) -> IntentMismatchDetectionResult:
        """Classify and evaluate intent mismatch severity fail-closed (Phase 199)."""
        now = datetime.now(UTC)
        match_res = request.match_result
        reason_codes: list[str] = []
        highest_severity = "NONE"

        for signal in match_res.signals:
            if signal.status == "MISMATCH":
                code, sev = self.SIGNAL_SEVERITY_MAP.get(
                    signal.dimension, ("INTENT_MISMATCH", "HIGH")
                )
                reason_codes.append(code)
                if self.SEVERITY_RANK.get(sev, 0) > self.SEVERITY_RANK.get(highest_severity, 0):
                    highest_severity = sev

        mismatch_detected = len(reason_codes) > 0
        # Fail closed: CRITICAL or HIGH mismatches halt policy execution (can_proceed = False)
        can_proceed = highest_severity not in ("CRITICAL", "HIGH")

        if mismatch_detected:
            explanation = f"Detected {len(reason_codes)} intent mismatch(es) with highest severity '{highest_severity}' ({', '.join(reason_codes)})."  # noqa: E501
        else:
            explanation = "No intent mismatches detected. Operation aligns with declared intent."

        return IntentMismatchDetectionResult(
            mismatch_detected=mismatch_detected,
            severity=highest_severity,
            reason_codes=reason_codes,
            can_proceed=can_proceed,
            explanation=explanation,
            evaluated_at=now,
        )
