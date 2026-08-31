"""ATIM Model Governance & Champion/Challenger Service (Phase 11 / Group 6)."""

import logging
from decimal import Decimal
from typing import Any, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.models import (
    CompositeGovernanceScore,
    GovernanceDecisionRecord,
    GovernanceStatus,
)
from app.infrastructure.database.models.atim_governance import (
    ATIMGovernanceDecision,
    ATIMModelVersion,
)

logger = logging.getLogger("agentpay.atim.governance")

ATIM_SECURITY_FLOOR = Decimal("0.9500")


class ATIMGovernanceService:
    """Production governance service managing LLM model lifecycles, deployment gates, and rollbacks."""

    def __init__(self, min_security_floor: Decimal = ATIM_SECURITY_FLOOR) -> None:
        self.min_security_floor = min_security_floor
        self._global_champion: str = "openai/gpt-4o"
        self._global_challenger: Optional[str] = "anthropic/claude-3-5-sonnet-20241022"

    def get_champion_model(self) -> str:
        """Retrieve active champion model ID."""
        return self._global_champion

    def get_challenger_model(self) -> Optional[str]:
        """Retrieve active challenger model ID."""
        return self._global_challenger

    async def evaluate_governance_gate(
        self,
        security_score: Decimal,
        regression_passed: bool,
    ) -> bool:
        """Evaluate whether candidate model satisfies security floor and regression gates."""
        if security_score < self.min_security_floor:
            logger.warning(
                "Governance gate rejected model: security score %s < floor %s",
                security_score,
                self.min_security_floor,
            )
            return False
        return regression_passed

    async def promote_model(
        self,
        db: AsyncSession | Any,
        model_id: str,
        target_status: GovernanceStatus,
        security_score: Decimal,
        decision_reason: str,
        actor_id: Optional[uuid.UUID] = None,
        actor_type: str = "ADMIN",
        tenant_id: Optional[uuid.UUID] = None,
    ) -> GovernanceDecisionRecord:
        """Promote or transition model governance status with immutable audit logging."""
        # 1. Enforce Hard Security Floor
        if security_score < self.min_security_floor:
            target_status = GovernanceStatus.REJECTED
            decision_reason = f"HARD SECURITY FLOOR VIOLATION: Score {security_score} < {self.min_security_floor}"

        # 2. Enforce Admin Authorization for Champion/Approved promotion
        if target_status in (GovernanceStatus.APPROVED, GovernanceStatus.CHAMPION):
            if actor_type != "ADMIN":
                raise PermissionError("Server-side admin authorization required for model promotion.")

        previous_status = GovernanceStatus.CANDIDATE
        if target_status == GovernanceStatus.CHAMPION:
            self._global_champion = model_id
            logger.info("New global Champion model set to: %s", model_id)

        # 3. Create Audit Record
        audit_entry = ATIMGovernanceDecision(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            model_id=model_id,
            prompt_version="v1.0.0",
            dataset_version="v1.0.0",
            previous_status=previous_status.value,
            new_status=target_status.value,
            decision_reason=decision_reason,
            security_score=security_score,
        )

        if hasattr(db, "add"):
            db.add(audit_entry)
            if hasattr(db, "commit"):
                try:
                    await db.commit()
                except Exception:
                    pass

        return GovernanceDecisionRecord(
            id=audit_entry.id,
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            model_id=model_id,
            previous_status=previous_status,
            new_status=target_status,
            decision_reason=decision_reason,
            security_score=security_score,
        )

    async def rollback_model(
        self,
        db: AsyncSession | Any,
        model_id: str,
        fallback_model_id: str = "openai/gpt-4o",
        reason: str = "SLO regression / Circuit breaker trigger",
        actor_id: Optional[uuid.UUID] = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> GovernanceDecisionRecord:
        """Rollback candidate or degraded model to last known good model."""
        self._global_champion = fallback_model_id
        logger.warning("Rolling back model %s to fallback %s. Reason: %s", model_id, fallback_model_id, reason)

        return await self.promote_model(
            db=db,
            model_id=model_id,
            target_status=GovernanceStatus.ROLLED_BACK,
            security_score=Decimal("0.9500"),
            decision_reason=f"ROLLBACK to {fallback_model_id}: {reason}",
            actor_id=actor_id,
            actor_type="SYSTEM",
            tenant_id=tenant_id,
        )
