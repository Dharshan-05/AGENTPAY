"""Policy Priority Application Service for AGENTPAY (Phase 196)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.schemas.policy_priority import (
    PolicyPriorityValidationRequest,
    PolicyPriorityValidationResult,
)

logger = logging.getLogger("agentguard.security.policy_priority_system")


class PolicyPriorityService:
    """Production Policy Priority Management & Sorting System (Phase 196 - Read/Decision Only)."""  # noqa: E501

    MIN_PRIORITY = 0
    MAX_PRIORITY = 10000

    def validate_priority(
        self,
        request: PolicyPriorityValidationRequest,
    ) -> PolicyPriorityValidationResult:
        """Validate proposed policy priority integer within bounds [0, 10000] (Phase 196)."""
        now = datetime.now(UTC)

        if request.priority < self.MIN_PRIORITY:
            return PolicyPriorityValidationResult(
                is_valid=False,
                priority=request.priority,
                reason_code="PRIORITY_BELOW_MINIMUM",
                explanation=f"Policy priority ({request.priority}) cannot be negative.",
                validated_at=now,
            )

        if request.priority > self.MAX_PRIORITY:
            return PolicyPriorityValidationResult(
                is_valid=False,
                priority=request.priority,
                reason_code="PRIORITY_EXCEEDS_MAXIMUM",
                explanation=f"Policy priority ({request.priority}) exceeds maximum allowed bound ({self.MAX_PRIORITY}).",  # noqa: E501
                validated_at=now,
            )

        return PolicyPriorityValidationResult(
            is_valid=True,
            priority=request.priority,
            reason_code="PRIORITY_VALID",
            explanation=f"Policy priority ({request.priority}) is within valid bounds.",
            validated_at=now,
        )

    def sort_policies_by_priority(self, policies: list[Any]) -> list[Any]:
        """Deterministically sort policies by priority DESC, then ID ASC tie-break (Phase 196)."""
        return sorted(
            policies,
            key=lambda p: (-getattr(p, "priority", 100), str(getattr(p, "id", ""))),
        )
