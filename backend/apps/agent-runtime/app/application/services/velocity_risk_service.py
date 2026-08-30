"""Velocity Risk Application Service for AGENTPAY (Phase 212)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.velocity_detection_service import VelocityDetectionService
from app.schemas.agent_risk_profile import RiskFactor
from app.schemas.velocity_detection import VelocityDetectionRequest
from app.schemas.velocity_risk import VelocityRiskRequest, VelocityRiskResult

logger = logging.getLogger("agentguard.security.velocity_risk")


class VelocityRiskService:
    """Production Velocity Risk Engine (Phase 212 - Read/Advisory Only)."""

    def __init__(self, velocity_service: VelocityDetectionService | None = None) -> None:
        self.velocity_service = velocity_service or VelocityDetectionService()

    async def calculate_velocity_risk(
        self,
        db: AsyncSession | Any,
        request: VelocityRiskRequest,
    ) -> VelocityRiskResult:
        """Calculate normalized velocity risk score for an agent (Phase 212)."""
        now = datetime.now(UTC)

        v_req = VelocityDetectionRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            window_minutes=request.window_minutes,
            max_allowed_count=request.max_allowed_count,
            max_allowed_amount=request.max_allowed_amount,
        )
        v_res = await self.velocity_service.detect_velocity(db, v_req)

        burst_detected = v_res.transaction_count >= 5 and request.window_minutes <= 15
        risk_score = v_res.velocity_score
        if burst_detected:
            risk_score = max(risk_score, Decimal("0.75"))

        risk_factors = [
            RiskFactor(
                code=rc, severity=v_res.severity, source="VELOCITY", confidence=Decimal("1.00")
            )
            for rc in v_res.reason_codes
        ]

        if burst_detected and "SHORT_WINDOW_BURST" not in v_res.reason_codes:
            risk_factors.append(
                RiskFactor(
                    code="SHORT_WINDOW_BURST",
                    severity="HIGH",
                    source="VELOCITY",
                    confidence=Decimal("1.00"),
                )
            )

        sev_map = {
            "NORMAL": "NORMAL",
            "LOW": "ELEVATED",
            "MEDIUM": "ELEVATED",
            "HIGH": "HIGH",
            "CRITICAL": "CRITICAL",
        }
        mapped_severity = sev_map.get(v_res.severity, "NORMAL")
        if burst_detected and mapped_severity not in ("HIGH", "CRITICAL"):
            mapped_severity = "HIGH"

        explanation = (
            f"Velocity evaluation in {request.window_minutes}m window: "
            f"{v_res.transaction_count} txs, total {v_res.total_amount} (Severity: {mapped_severity})."  # noqa: E501
        )

        return VelocityRiskResult(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            velocity_risk_score=risk_score,
            severity=mapped_severity,
            burst_detected=burst_detected,
            window_minutes=request.window_minutes,
            risk_factors=risk_factors,
            explanation=explanation,
            evaluated_at=now,
        )
