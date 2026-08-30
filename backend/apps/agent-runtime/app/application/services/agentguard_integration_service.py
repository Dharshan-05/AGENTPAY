"""AgentGuard Integration Application Service for AGENTPAY (Phase 215)."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agentguard_decision_service import AgentGuardDecisionService
from app.schemas.agentguard_decision import (
    AgentGuardDecisionRequest,
    AgentGuardDecisionResult,
)

logger = logging.getLogger("agentguard.security.integration")


class AgentGuardIntegrationService:
    """Production AgentGuard Security Foundation Integration Gateway (Phase 215)."""

    def __init__(self, decision_service: AgentGuardDecisionService | None = None) -> None:
        self.decision_service = decision_service or AgentGuardDecisionService()

    async def evaluate_agent_request(
        self,
        db: AsyncSession | Any,
        request: AgentGuardDecisionRequest,
    ) -> AgentGuardDecisionResult:
        """Evaluate agent request through unified AGENTGUARD security foundation (Phase 215)."""  # noqa: E501
        logger.info(
            "Executing AGENTGUARD security integration evaluation for agent %s in tenant %s",  # noqa: E501
            request.agent_id,
            request.tenant_id,
        )
        return await self.decision_service.evaluate_agentguard_decision(db, request)
