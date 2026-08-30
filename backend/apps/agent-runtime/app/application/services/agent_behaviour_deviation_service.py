"""Agent Behaviour Deviation application service for AGENTPAY (Phase 136).

Responsibilities:
    - Establish baseline from historical `BehaviourEvent` & `CommerceTransaction` records
    - Evaluate recent activity window against historical baseline
    - Calculate explainable deviation score (0.00 - 100.00) and severity
    - Read/analysis-oriented: MUST NOT mutate agent lifecycle status or revoke credentials
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.behaviour_event import BehaviourEvent
from app.schemas.agents import AgentBehaviourDeviationResponse

logger = logging.getLogger("agentpay.agent.behaviour_deviation.service")


class AgentBehaviourDeviationService:
    """Application service for calculating Agent Behaviour Deviation (Phase 136)."""

    def __init__(
        self,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def calculate_deviation(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentBehaviourDeviationResponse:
        """Calculate deterministic behaviour deviation for an agent within tenant scope.

        Raises:
            AgentNotFoundError: if agent does not exist or belongs to another tenant.
        """
        # 1. IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        now = datetime.now(UTC)
        recent_window_start = now - timedelta(hours=24)
        historical_window_start = now - timedelta(days=30)

        # 2. Historical Baseline: Avg daily event count in past 30 days
        hist_stmt = select(func.count(BehaviourEvent.id)).where(
            BehaviourEvent.agent_id == agent_id,
            BehaviourEvent.tenant_id == tenant_id,
            BehaviourEvent.occurred_at >= historical_window_start,
            BehaviourEvent.occurred_at < recent_window_start,
        )
        hist_res = await db.execute(hist_stmt)
        hist_count = hist_res.scalar() or 0
        baseline_daily_avg = (
            Decimal(str(round(hist_count / 29.0, 2))) if hist_count > 0 else Decimal("5.00")
        )

        # 3. Recent Activity: Count of events in past 24 hours
        rec_stmt = select(func.count(BehaviourEvent.id)).where(
            BehaviourEvent.agent_id == agent_id,
            BehaviourEvent.tenant_id == tenant_id,
            BehaviourEvent.occurred_at >= recent_window_start,
        )
        rec_res = await db.execute(rec_stmt)
        recent_count = rec_res.scalar() or 0
        observed_value = Decimal(str(recent_count))

        # 4. Deterministic Deviation Calculation
        # Expected range: baseline_daily_avg ± 50%
        range_min = max(Decimal("0.00"), baseline_daily_avg * Decimal("0.50"))
        range_max = baseline_daily_avg * Decimal("2.00") + Decimal("10.00")
        expected_range_str = f"{range_min:.2f} - {range_max:.2f}"

        if observed_value > range_max:
            multiplier = observed_value / (range_max if range_max > 0 else Decimal("1.00"))
            score = min(
                Decimal("100.00"),
                (multiplier - Decimal("1.00")) * Decimal("40.00") + Decimal("50.00"),
            )
            severity = "high" if score >= Decimal("75.00") else "medium"
            reason = (
                f"Observed activity ({observed_value:.0f} events/24h) "
                f"exceeded expected range ({expected_range_str})."
            )
        elif observed_value < range_min and baseline_daily_avg > Decimal("10.00"):
            score = Decimal("30.00")
            severity = "low"
            reason = (
                f"Observed activity ({observed_value:.0f} events/24h) "
                f"below baseline range ({expected_range_str})."
            )
        else:
            score = Decimal("0.00")
            severity = "low"
            reason = (
                f"Observed activity ({observed_value:.0f} events/24h) "
                f"within expected range ({expected_range_str})."
            )

        # 5. Integrate Audit Log for high deviation
        if severity in ("medium", "high"):
            await self.audit_service.record_audit_event(
                db,
                tenant_id,
                agent_id,
                agent_id,
                event_type="status_changed",
                event_action="behaviour_deviation_detected",
                event_result="success",
                event_metadata={
                    "deviation_score": str(score),
                    "severity": severity,
                    "reason": reason,
                },
            )

        logger.info(
            "Agent behaviour deviation evaluated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "deviation_score": str(score),
                "severity": severity,
            },
        )

        return AgentBehaviourDeviationResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            baseline_reference="30-day historical daily event frequency",
            observed_value=observed_value,
            expected_range=expected_range_str,
            deviation_score=score.quantize(Decimal("0.01")),
            deviation_type="frequency",
            severity=severity,
            reason=reason,
            evaluated_at=now,
        )
