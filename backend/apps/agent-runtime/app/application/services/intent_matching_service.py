"""Intent Matching Application Service for AGENTPAY (Phase 198)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.intent_matching import (
    IntentMatchRequest,
    IntentMatchResult,
    IntentMatchSignal,
)

logger = logging.getLogger("agentguard.security.intent_matching")


class IntentMatchingService:
    """Production Intent Matching Engine (Phase 198 - Read/Decision Only)."""

    def match_intent(
        self,
        request: IntentMatchRequest,
    ) -> IntentMatchResult:
        """Compare declared intent against requested operation deterministically (Phase 198)."""
        now = datetime.now(UTC)
        intent = request.declared_intent
        signals: list[IntentMatchSignal] = []
        has_critical_mismatch = False

        # 1. Action Signal (Weight 0.25)
        dec_act = (intent.action or "").strip().lower()
        req_act = (request.requested_action or "").strip().lower()
        if dec_act in ("pay", "payment", "purchase", "buy"):
            dec_act = "payment"
        if req_act in ("pay", "payment", "purchase", "buy"):
            req_act = "payment"

        if dec_act == req_act:
            signals.append(
                IntentMatchSignal(
                    dimension="action",
                    status="EXACT_MATCH",
                    weight=Decimal("0.25"),
                    score=Decimal("1.00"),
                    detail=f"Action '{request.requested_action}' matches declared intent.",
                )
            )
        else:
            has_critical_mismatch = True
            signals.append(
                IntentMatchSignal(
                    dimension="action",
                    status="MISMATCH",
                    weight=Decimal("0.25"),
                    score=Decimal("0.00"),
                    detail=f"Action '{request.requested_action}' does not match declared '{intent.action}'.",  # noqa: E501
                )
            )

        # 2. Currency Signal (Weight 0.20)
        dec_curr = (intent.currency or "USD").strip().upper()
        req_curr = (request.requested_currency or "USD").strip().upper()
        if dec_curr == req_curr:
            signals.append(
                IntentMatchSignal(
                    dimension="currency",
                    status="EXACT_MATCH",
                    weight=Decimal("0.20"),
                    score=Decimal("1.00"),
                    detail=f"Currency '{req_curr}' matches declared intent.",
                )
            )
        else:
            has_critical_mismatch = True
            signals.append(
                IntentMatchSignal(
                    dimension="currency",
                    status="MISMATCH",
                    weight=Decimal("0.20"),
                    score=Decimal("0.00"),
                    detail=f"Currency '{req_curr}' does not match declared '{dec_curr}'.",
                )
            )

        # 3. Amount Signal (Weight 0.25)
        if intent.amount is not None and request.requested_amount is not None:
            if request.requested_amount <= intent.amount:
                signals.append(
                    IntentMatchSignal(
                        dimension="amount",
                        status="EXACT_MATCH",
                        weight=Decimal("0.25"),
                        score=Decimal("1.00"),
                        detail=f"Amount {request.requested_amount} is within declared intent limit {intent.amount}.",  # noqa: E501
                    )
                )
            else:
                has_critical_mismatch = True
                signals.append(
                    IntentMatchSignal(
                        dimension="amount",
                        status="MISMATCH",
                        weight=Decimal("0.25"),
                        score=Decimal("0.00"),
                        detail=f"Requested amount {request.requested_amount} exceeds declared limit {intent.amount}.",  # noqa: E501
                    )
                )
        else:
            signals.append(
                IntentMatchSignal(
                    dimension="amount",
                    status="NOT_APPLICABLE",
                    weight=Decimal("0.25"),
                    score=Decimal("1.00"),
                    detail="No amount restriction declared.",
                )
            )

        # 4. Merchant Signal (Weight 0.15)
        dec_m = (
            str(intent.merchant_id).lower()
            if intent.merchant_id
            else (intent.merchant_slug or "").strip().lower()
        )  # noqa: E501
        req_m = (request.requested_merchant_id or "").strip().lower()
        if dec_m and req_m:
            if dec_m == req_m:
                signals.append(
                    IntentMatchSignal(
                        dimension="merchant",
                        status="EXACT_MATCH",
                        weight=Decimal("0.15"),
                        score=Decimal("1.00"),
                        detail=f"Merchant '{request.requested_merchant_id}' matches declared intent.",  # noqa: E501
                    )
                )
            else:
                has_critical_mismatch = True
                signals.append(
                    IntentMatchSignal(
                        dimension="merchant",
                        status="MISMATCH",
                        weight=Decimal("0.15"),
                        score=Decimal("0.00"),
                        detail=f"Merchant '{request.requested_merchant_id}' does not match declared '{dec_m}'.",  # noqa: E501
                    )
                )
        else:
            signals.append(
                IntentMatchSignal(
                    dimension="merchant",
                    status="NOT_APPLICABLE",
                    weight=Decimal("0.15"),
                    score=Decimal("1.00"),
                    detail="No merchant restriction declared.",
                )
            )

        # 5. Category Signal (Weight 0.15)
        dec_c = (intent.category or "").strip().lower()
        req_c = (request.requested_category or "").strip().lower()
        if dec_c and req_c:
            if req_c == dec_c or req_c.startswith(f"{dec_c}."):
                signals.append(
                    IntentMatchSignal(
                        dimension="category",
                        status="EXACT_MATCH",
                        weight=Decimal("0.15"),
                        score=Decimal("1.00"),
                        detail=f"Category '{request.requested_category}' matches declared intent.",
                    )
                )
            else:
                signals.append(
                    IntentMatchSignal(
                        dimension="category",
                        status="MISMATCH",
                        weight=Decimal("0.15"),
                        score=Decimal("0.00"),
                        detail=f"Category '{request.requested_category}' does not match declared '{intent.category}'.",  # noqa: E501
                    )
                )
        else:
            signals.append(
                IntentMatchSignal(
                    dimension="category",
                    status="NOT_APPLICABLE",
                    weight=Decimal("0.15"),
                    score=Decimal("1.00"),
                    detail="No category restriction declared.",
                )
            )

        # Compute Total Weighted Match Score
        if has_critical_mismatch:
            overall_match = "MISMATCH"
            match_score = Decimal("0.00")
        else:
            total = sum((s.weight * s.score for s in signals), Decimal("0.00"))
            match_score = round(total, 2)
            if match_score == Decimal("1.00"):
                overall_match = "EXACT_MATCH"
            else:
                overall_match = "PARTIAL_MATCH"

        return IntentMatchResult(
            overall_match=overall_match,
            match_score=match_score,
            signals=signals,
            evaluated_at=now,
        )
