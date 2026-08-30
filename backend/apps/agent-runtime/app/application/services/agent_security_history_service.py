"""Agent Security History Application Service for AGENTPAY (Phase 210)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_violation_tracking_service import (
    AgentViolationTrackingService,
)
from app.schemas.agent_security_history import AgentSecurityHistorySummary
from app.schemas.agent_violations import AgentViolationQueryRequest

logger = logging.getLogger("agentguard.security.agent_security_history")


class AgentSecurityHistoryService:
    """Production Agent Security History Service (Phase 210 - Read/Query Only)."""

    def __init__(self, violation_service: AgentViolationTrackingService | None = None) -> None:
        self.violation_service = violation_service or AgentViolationTrackingService()

    async def get_security_history_summary(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentSecurityHistorySummary:
        """Construct structured security history view for an agent (Phase 210)."""
        now = datetime.now(UTC)

        query_req = AgentViolationQueryRequest(tenant_id=tenant_id, agent_id=agent_id, limit=100)
        v_res = await self.violation_service.get_agent_violations(db, query_req)
        violations = v_res.violations

        sev_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        timeline: list[dict[str, str]] = []
        for v in violations:
            if v.severity in sev_dist:
                sev_dist[v.severity] += 1
            timeline.append(
                {
                    "event_id": str(v.violation_id),
                    "type": v.violation_type,
                    "severity": v.severity,
                    "occurred_at": v.occurred_at.isoformat(),
                }
            )

        if sev_dist["CRITICAL"] > 0 or sev_dist["HIGH"] >= 3:
            trend = "DETERIORATING"
        elif sum(sev_dist.values()) == 0:
            trend = "STABLE"
        else:
            trend = "STABLE"

        return AgentSecurityHistorySummary(
            agent_id=agent_id,
            tenant_id=tenant_id,
            total_events=len(violations),
            denial_count=sum(1 for v in violations if "DENY" in v.violation_type),
            violation_count=len(violations),
            mismatch_count=sum(1 for v in violations if "MISMATCH" in v.violation_type),
            recent_severity_distribution=sev_dist,
            historical_trend=trend,
            unresolved_incidents=sum(1 for v in violations if v.status == "ACTIVE"),
            timeline_summary=timeline[:10],
            evaluated_at=now,
        )
