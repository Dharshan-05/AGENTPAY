"""Transaction Threshold Evaluation Service for AGENTPAY (Phase 191)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.transaction_thresholds import (
    TransactionThresholdEvaluationRequest,
    TransactionThresholdEvaluationResult,
)

logger = logging.getLogger("agentguard.security.transaction_threshold_service")


class TransactionThresholdService:
    """Production Transaction Threshold Evaluation Engine (Phase 191 - Read/Decision Only)."""

    def evaluate_threshold(
        self,
        request: TransactionThresholdEvaluationRequest,
    ) -> TransactionThresholdEvaluationResult:
        """Evaluate transaction amount against configured thresholds (Phase 191)."""
        now = datetime.now(UTC)

        # 1. Invalid amount check (Decimal precision)
        if request.amount <= Decimal("0.00"):
            return TransactionThresholdEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                currency=request.currency,
                decision="DENIED",
                reason_code="INVALID_AMOUNT",
                explanation="Transaction amount must be strictly greater than zero.",
                evaluated_at=now,
            )

        # 2. Currency mismatch validation (Fail-closed)
        if request.currency.strip().upper() != request.threshold_currency.strip().upper():
            logger.warning(
                "Transaction threshold currency mismatch: tx %s != threshold %s",
                request.currency,
                request.threshold_currency,
            )
            return TransactionThresholdEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                currency=request.currency,
                decision="DENIED",
                reason_code="INVALID_CURRENCY",
                explanation=f"Currency mismatch: transaction currency ({request.currency}) != threshold currency ({request.threshold_currency}).",  # noqa: E501
                evaluated_at=now,
            )

        # 3. Minimum threshold check
        if request.minimum_amount is not None and request.amount < request.minimum_amount:
            return TransactionThresholdEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                currency=request.currency,
                decision="DENIED",
                reason_code="MINIMUM_THRESHOLD_BREACH",
                explanation=f"Transaction amount ({request.amount} {request.currency}) is below minimum threshold ({request.minimum_amount} {request.currency}).",  # noqa: E501
                evaluated_at=now,
            )

        # 4. Maximum hard denial threshold check
        if request.maximum_amount is not None and request.amount > request.maximum_amount:
            return TransactionThresholdEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                currency=request.currency,
                decision="DENIED",
                reason_code="MAXIMUM_THRESHOLD_EXCEEDED",
                explanation=f"Transaction amount ({request.amount} {request.currency}) exceeds maximum allowed threshold ({request.maximum_amount} {request.currency}).",  # noqa: E501
                evaluated_at=now,
            )

        # 5. Approval threshold check
        if request.approval_threshold is not None and request.amount > request.approval_threshold:
            return TransactionThresholdEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                amount=request.amount,
                currency=request.currency,
                decision="REQUIRE_APPROVAL",
                reason_code="APPROVAL_THRESHOLD_EXCEEDED",
                explanation=f"Transaction amount ({request.amount} {request.currency}) exceeds approval threshold ({request.approval_threshold} {request.currency}). Human approval required.",  # noqa: E501
                evaluated_at=now,
            )

        # 6. Below all thresholds -> ALLOW
        return TransactionThresholdEvaluationResult(
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            amount=request.amount,
            currency=request.currency,
            decision="ALLOW",
            reason_code="BELOW_THRESHOLD",
            explanation=f"Transaction amount ({request.amount} {request.currency}) is within all configured thresholds.",  # noqa: E501
            evaluated_at=now,
        )
