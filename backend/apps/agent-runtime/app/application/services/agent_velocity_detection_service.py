"""Agent Velocity Detection application service for AGENTPAY (Phase 137).

Responsibilities:
    - Bounded time-window velocity metrics calculation across agent activity
    - Evaluates transaction volume and monetary amount against configurable thresholds
    - Handles edge cases: empty windows, zero activity, exact threshold, threshold exceeded
    - Read/analysis-oriented: MUST NOT mutate agent status or reject payments directly
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
from app.schemas.agents import AgentVelocityDetectionResponse

logger = logging.getLogger("agentpay.agent.velocity_detection.service")

# Default velocity thresholds per window
WINDOW_CONFIGS: dict[str, dict[str, Any]] = {
    "1h": {"hours": 1, "threshold_count": 50, "threshold_amount": Decimal("10000.00")},
    "24h": {"hours": 24, "threshold_count": 200, "threshold_amount": Decimal("50000.00")},
    "7d": {"hours": 168, "threshold_count": 1000, "threshold_amount": Decimal("250000.00")},
}


class AgentVelocityDetectionService:
    """Application service for calculating Agent Velocity Detection (Phase 137)."""

    def __init__(
        self,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def detect_velocity(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        window: str = "24h",
        custom_threshold_count: int | None = None,
        custom_threshold_amount: Decimal | None = None,
    ) -> AgentVelocityDetectionResponse:
        """Calculate agent activity velocity metrics within bounded time window.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
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

        win_key = window.strip().lower()
        cfg = WINDOW_CONFIGS.get(win_key, WINDOW_CONFIGS["24h"])
        hours_back = cfg["hours"]
        thresh_count = custom_threshold_count or cfg["threshold_count"]
        thresh_amount = custom_threshold_amount or cfg["threshold_amount"]

        now = datetime.now(UTC)
        window_start = now - timedelta(hours=hours_back)

        # 2. Query transactions in bounded window
        tx_stmt = select(
            func.count(CommerceTransaction.id).label("tx_count"),
            func.coalesce(func.sum(CommerceTransaction.amount), 0.00).label("tx_sum"),
        ).where(
            CommerceTransaction.agent_id == agent_id,
            CommerceTransaction.tenant_id == tenant_id,
            CommerceTransaction.created_at >= window_start,
        )
        tx_res = await db.execute(tx_stmt)
        row = tx_res.one()
        obs_count = int(row.tx_count or 0)
        obs_amount = Decimal(str(row.tx_sum or "0.00"))

        # 3. Velocity Score & Severity Calculation
        count_ratio = (
            Decimal(str(obs_count)) / Decimal(str(thresh_count))
            if thresh_count > 0
            else Decimal("0.00")
        )
        amount_ratio = (
            obs_amount / thresh_amount if thresh_amount > Decimal("0.00") else Decimal("0.00")
        )
        max_ratio = max(count_ratio, amount_ratio)

        if max_ratio > Decimal("1.00"):
            velocity_score = min(Decimal("100.00"), max_ratio * Decimal("50.00"))
            severity = "critical" if velocity_score >= Decimal("90.00") else "high"
            reason = (
                f"Velocity threshold exceeded in {win_key} window: observed {obs_count} txs "
                f"(${obs_amount:.2f}) vs limit {thresh_count} txs (${thresh_amount:.2f})."
            )
        elif max_ratio == Decimal("1.00"):
            velocity_score = Decimal("50.00")
            severity = "medium"
            reason = f"Velocity exactly at threshold limit in {win_key} window ({obs_count} txs)."
        elif max_ratio >= Decimal("0.80"):
            velocity_score = Decimal("40.00")
            severity = "medium"
            reason = f"Velocity approaching threshold limit in {win_key} window."
        else:
            velocity_score = Decimal("0.00")
            severity = "low"
            reason = f"Normal activity velocity in {win_key} window."

        # 4. Record Security Event if threshold exceeded
        if max_ratio >= Decimal("1.00"):
            await self.security_event_service.record_security_event(
                db,
                tenant_id,
                agent_id=agent_id,
                event_type="suspicious_activity",
                event_action="security_control_triggered",
                event_result="detected",
                severity=severity,
                event_payload={
                    "window": win_key,
                    "observed_count": obs_count,
                    "observed_amount": str(obs_amount),
                    "threshold_count": thresh_count,
                    "threshold_amount": str(thresh_amount),
                },
            )

        logger.info(
            "Agent velocity evaluated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "window": win_key,
                "velocity_score": str(velocity_score),
                "severity": severity,
            },
        )

        return AgentVelocityDetectionResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            window=win_key,
            observed_count=obs_count,
            observed_amount=obs_amount.quantize(Decimal("0.01")),
            threshold_count=thresh_count,
            threshold_amount=thresh_amount.quantize(Decimal("0.01")),
            velocity_score=velocity_score.quantize(Decimal("0.01")),
            severity=severity,
            detection_type="transaction_velocity",
            reason=reason,
            evaluated_at=now,
        )
