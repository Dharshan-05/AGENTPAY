"""Agent Trust Score Application Service for AGENTPAY (Phase 206)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.agent_trust_score import AgentTrustScore, TrustDimension

logger = logging.getLogger("agentguard.security.agent_trust_score")


class AgentTrustScoreService:
    """Production Agent Trust Score Foundation Service (Phase 206 - Advisory Subsystem)."""

    def create_trust_score(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        trust_score: Decimal,
        dimensions: list[TrustDimension] | None = None,
        confidence: Decimal = Decimal("1.00"),
        contributing_signals: dict[str, str] | None = None,
    ) -> AgentTrustScore:
        """Construct a bounded, deterministic AgentTrustScore (Phase 206)."""
        now = datetime.now(UTC)
        clamped_score = max(Decimal("0.00"), min(Decimal("1.00"), trust_score))
        clamped_confidence = max(Decimal("0.00"), min(Decimal("1.00"), confidence))

        if clamped_confidence < Decimal("0.30"):
            state = "COLD_START"
        elif clamped_score >= Decimal("0.85"):
            state = "TRUSTED"
        elif clamped_score >= Decimal("0.65"):
            state = "NORMAL"
        elif clamped_score >= Decimal("0.45"):
            state = "LOW_TRUST"
        elif clamped_score >= Decimal("0.25"):
            state = "HIGH_RISK"
        else:
            state = "UNTRUSTED"

        return AgentTrustScore(
            agent_id=agent_id,
            tenant_id=tenant_id,
            trust_score=clamped_score,
            confidence=clamped_confidence,
            trust_state=state,
            dimensions=dimensions or [],
            score_version="2.0",
            evaluated_at=now,
            contributing_signal_summary=contributing_signals or {},
        )
