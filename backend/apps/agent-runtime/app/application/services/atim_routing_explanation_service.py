"""ATIM Auditable Routing Explanation Generator Service (Phase 12 / Group 6)."""

import logging
from decimal import Decimal
from typing import Any, Optional
import uuid

from app.domain.governance.models import RoutingExplanationRecord

logger = logging.getLogger("agentpay.atim.routing_explanation")


class ATIMRoutingExplanationService:
    """Service producing structured, auditable routing explanations for model selections and fallbacks."""

    def build_explanation(
        self,
        request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        selected_model: str,
        provider: str,
        task_type: str,
        risk_level: str,
        eligible_models: list[str],
        rejected_models: dict[str, str],
        routing_scores: dict[str, float],
        cost_estimate_usd: Decimal,
        latency_estimate_ms: float,
        security_score: Decimal,
        fallback_chain: list[str],
        decision_reason: str,
    ) -> RoutingExplanationRecord:
        """Construct an immutable, auditable routing decision explanation object."""
        # Sanitize sensitive reasons if any
        sanitized_rejected = {
            m: reason[:256] for m, reason in rejected_models.items()
        }

        explanation = RoutingExplanationRecord(
            request_id=request_id,
            tenant_id=tenant_id,
            selected_model=selected_model,
            provider=provider,
            task_type=task_type,
            risk_level=risk_level,
            eligible_models=eligible_models,
            rejected_models=sanitized_rejected,
            routing_scores=routing_scores,
            cost_estimate_usd=cost_estimate_usd,
            latency_estimate_ms=latency_estimate_ms,
            security_score=security_score,
            fallback_chain=fallback_chain,
            decision_reason=decision_reason[:512],
        )

        logger.info(
            "Built routing explanation for request %s (Tenant %s): Selected model '%s' via provider '%s'. Reason: %s",
            request_id,
            tenant_id,
            selected_model,
            provider,
            decision_reason,
        )

        return explanation
