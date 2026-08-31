"""ATIM Abuse Prevention & Escalation Subsystem (Phase 18 / Group 9)."""

import logging
from typing import Optional
import uuid

from app.domain.governance.policy_models import AbuseAction, AbuseEventRecord, AbuseSeverity

logger = logging.getLogger("agentpay.atim.abuse_detection")


class ATIMAbuseDetectionService:
    """Service evaluating continuous abuse patterns and triggering deterministic escalation actions."""

    def __init__(self) -> None:
        self._abuse_scores: dict[uuid.UUID, int] = {}

    def record_abuse_signal(
        self,
        tenant_id: uuid.UUID,
        abuse_type: str,
        score_increment: int = 10,
        agent_id: Optional[uuid.UUID] = None,
    ) -> AbuseEventRecord:
        """Record an abuse signal and determine escalation action based on accumulated threat score."""
        current_score = self._abuse_scores.get(tenant_id, 0) + score_increment
        self._abuse_scores[tenant_id] = current_score

        severity = AbuseSeverity.LOW
        action = AbuseAction.ALLOW

        if current_score >= 100:
            severity = AbuseSeverity.CRITICAL
            action = AbuseAction.PERMANENT_SECURITY_BLOCK
        elif current_score >= 50:
            severity = AbuseSeverity.HIGH
            action = AbuseAction.REQUIRE_HITL
        elif current_score >= 30:
            severity = AbuseSeverity.MEDIUM
            action = AbuseAction.THROTTLE

        record = AbuseEventRecord(
            tenant_id=tenant_id,
            agent_id=agent_id,
            abuse_type=abuse_type,
            severity=severity,
            escalation_action=action,
            details=f"Accumulated abuse score {current_score} triggered action {action.value}",
        )

        logger.warning(
            "Abuse signal for Tenant %s [%s]: Score=%d, Severity=%s, Action=%s",
            tenant_id,
            abuse_type,
            current_score,
            severity.value,
            action.value,
        )

        return record
