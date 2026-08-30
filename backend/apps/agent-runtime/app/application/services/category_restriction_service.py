"""Category Restriction Evaluation Service for AGENTPAY (Phase 192)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.schemas.category_restrictions import (
    CategoryRestrictionEvaluationRequest,
    CategoryRestrictionEvaluationResult,
)

logger = logging.getLogger("agentguard.security.category_restriction_service")


class CategoryRestrictionService:
    """Production Category Restriction Evaluation Engine (Phase 192 - Read/Decision Only)."""

    def evaluate_category_restriction(
        self,
        request: CategoryRestrictionEvaluationRequest,
    ) -> CategoryRestrictionEvaluationResult:
        """Evaluate product/merchant category against allowlist & denylist rules (Phase 192)."""
        now = datetime.now(UTC)

        # 1. Missing category handling (Fail-closed if allowlist present)
        if not request.category or not request.category.strip():
            if request.allowed_categories:
                return CategoryRestrictionEvaluationResult(
                    agent_id=request.agent_id,
                    tenant_id=request.tenant_id,
                    category=None,
                    decision="DENIED",
                    reason_code="CATEGORY_MISSING",
                    explanation="Category information is missing but restrictive allowlist policies apply.",  # noqa: E501
                    evaluated_at=now,
                )
            return CategoryRestrictionEvaluationResult(
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                category=None,
                decision="ALLOW",
                reason_code="CATEGORY_NOT_RESTRICTED",
                explanation="No category provided and no category restrictions configured.",
                evaluated_at=now,
            )

        # 2. Case & whitespace normalization (hierarchical support)
        norm_cat = request.category.strip().lower()
        norm_allowed = [c.strip().lower() for c in request.allowed_categories if c.strip()]
        norm_blocked = [c.strip().lower() for c in request.blocked_categories if c.strip()]

        # 3. Explicit Denylist Precedence Check (DENY > ALLOW)
        for b in norm_blocked:
            if norm_cat == b or norm_cat.startswith(f"{b}."):
                return CategoryRestrictionEvaluationResult(
                    agent_id=request.agent_id,
                    tenant_id=request.tenant_id,
                    category=request.category,
                    decision="DENIED",
                    reason_code="CATEGORY_DENIED",
                    explanation=f"Category '{request.category}' is explicitly blocked by policy rule '{b}'.",  # noqa: E501
                    evaluated_at=now,
                )

        # 4. Explicit Allowlist Check
        if norm_allowed:
            is_allowed = False
            for a in norm_allowed:
                if norm_cat == a or norm_cat.startswith(f"{a}."):
                    is_allowed = True
                    break

            if not is_allowed:
                return CategoryRestrictionEvaluationResult(
                    agent_id=request.agent_id,
                    tenant_id=request.tenant_id,
                    category=request.category,
                    decision="DENIED",
                    reason_code="CATEGORY_NOT_ALLOWED",
                    explanation=f"Category '{request.category}' is not present in policy allowlist.",  # noqa: E501
                    evaluated_at=now,
                )

        # 5. Passed all restriction checks -> ALLOW
        return CategoryRestrictionEvaluationResult(
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            category=request.category,
            decision="ALLOW",
            reason_code="CATEGORY_ALLOWED",
            explanation=f"Category '{request.category}' is permitted by policy.",
            evaluated_at=now,
        )
