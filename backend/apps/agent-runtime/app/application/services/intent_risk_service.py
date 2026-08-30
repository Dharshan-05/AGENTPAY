"""Intent Risk Application Service for AGENTPAY (Phase 213)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.application.services.intent_matching_service import IntentMatchingService
from app.application.services.intent_mismatch_detection_service import (
    IntentMismatchDetectionService,
)
from app.application.services.intent_verification_service import IntentVerificationService
from app.schemas.agent_risk_profile import RiskFactor
from app.schemas.intent_matching import IntentMatchRequest
from app.schemas.intent_mismatch import IntentMismatchDetectionRequest
from app.schemas.intent_risk import IntentRiskRequest, IntentRiskResult
from app.schemas.intent_verification import DeclaredIntent, IntentVerificationRequest

logger = logging.getLogger("agentguard.security.intent_risk")


class IntentRiskService:
    """Production Intent Risk Engine (Phase 213 - Security Decision Subsystem)."""

    def __init__(
        self,
        verification_service: IntentVerificationService | None = None,
        matching_service: IntentMatchingService | None = None,
        mismatch_service: IntentMismatchDetectionService | None = None,
    ) -> None:
        self.verification_service = verification_service or IntentVerificationService()
        self.matching_service = matching_service or IntentMatchingService()
        self.mismatch_service = mismatch_service or IntentMismatchDetectionService()

    def calculate_intent_risk(
        self,
        request: IntentRiskRequest,
    ) -> IntentRiskResult:
        """Calculate normalized intent risk for an agent commercial request (Phase 213)."""
        now = datetime.now(UTC)

        if not request.declared_intent:
            return IntentRiskResult(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                intent_risk_score=Decimal("0.00"),
                severity="VERIFIED",
                risk_factors=[],
                can_proceed=True,
                explanation="No declared intent provided; default verification bypass.",
                evaluated_at=now,
            )

        declared_obj = DeclaredIntent(**request.declared_intent)
        iv_req = IntentVerificationRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            declared_intent=declared_obj,
            requested_action=request.requested_action,
            requested_amount=request.requested_amount,
            requested_currency=request.requested_currency,
            requested_merchant_id=(
                uuid.UUID(request.requested_merchant_id) if request.requested_merchant_id else None
            ),
            requested_category=request.requested_category,
        )
        iv_res = self.verification_service.verify_intent(iv_req)

        im_req = IntentMatchRequest(
            declared_intent=declared_obj,
            requested_action=request.requested_action,
            requested_amount=request.requested_amount,
            requested_currency=request.requested_currency,
            requested_merchant_id=request.requested_merchant_id,
            requested_category=request.requested_category,
        )
        im_res = self.matching_service.match_intent(im_req)

        det_req = IntentMismatchDetectionRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            match_result=im_res,
        )
        det_res = self.mismatch_service.detect_mismatches(det_req)

        risk_score = round(Decimal("1.00") - im_res.match_score, 2)
        risk_factors = [
            RiskFactor(
                code=rc,
                severity=det_res.severity,
                source="INTENT",
                confidence=Decimal("1.00"),
            )
            for rc in det_res.reason_codes
        ]

        can_proceed = det_res.can_proceed and iv_res.verified
        mapped_severity = det_res.severity if det_res.severity != "NONE" else "VERIFIED"

        return IntentRiskResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            intent_risk_score=risk_score,
            severity=mapped_severity,
            risk_factors=risk_factors,
            can_proceed=can_proceed,
            explanation=det_res.explanation,
            evaluated_at=now,
        )
