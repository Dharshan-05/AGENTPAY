"""Policy Conflict Resolution Application Service for AGENTPAY (Phase 195)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.schemas.policy_conflict_resolution import (
    PolicyCandidate,
    PolicyConflictResolutionResult,
)

logger = logging.getLogger("agentguard.security.policy_conflict_resolution")


class PolicyConflictResolutionService:
    """Production Policy Conflict Resolution Engine (Phase 195 - Read/Decision Only)."""

    DECISION_RANK = {
        "DENY": 3,
        "DENIED": 3,
        "REQUIRE_APPROVAL": 2,
        "REQUIRES_APPROVAL": 2,
        "ALLOW": 1,
    }

    def resolve_conflicts(
        self,
        candidates: list[PolicyCandidate],
    ) -> PolicyConflictResolutionResult:
        """Deterministically resolve competing policy decisions using DENY > REQUIRE_APPROVAL > ALLOW precedence (Phase 195)."""  # noqa: E501
        now = datetime.now(UTC)

        if not candidates:
            return PolicyConflictResolutionResult(
                decision="NO_APPLICABLE_POLICY",
                winning_policy_id=None,
                winning_rule_id=None,
                conflicting_policy_ids=[],
                conflict_detected=False,
                resolution_reason="No applicable policy candidates provided for resolution.",
                evaluated_at=now,
            )

        distinct_decisions = {c.decision for c in candidates}
        conflict_detected = len(distinct_decisions) > 1 or len(candidates) > 1

        # Sort candidates deterministically:
        # 1. Decision Rank (DENY [3] > REQUIRE_APPROVAL [2] > ALLOW [1])
        # 2. Priority (Numeric DESC, higher beats lower)
        # 3. Specificity (Merchant [3] > Category [2] > Global [1])
        # 4. UUID tie-break (str(id) ASC)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (
                -self.DECISION_RANK.get(c.decision, 0),
                -c.priority,
                -c.specificity,
                str(c.policy_id),
            ),
        )

        winner = sorted_candidates[0]
        conflicting_ids = list(dict.fromkeys([c.policy_id for c in candidates]))

        if winner.decision == "DENIED" or winner.decision == "DENY":
            if "ALLOW" in distinct_decisions:
                reason_str = "DENY_OVERRIDES_ALLOW: Explicit DENY policy takes deterministic precedence over ALLOW."  # noqa: E501
            elif "REQUIRE_APPROVAL" in distinct_decisions:
                reason_str = "DENY_OVERRIDES_APPROVAL: Explicit DENY policy takes deterministic precedence over REQUIRE_APPROVAL."  # noqa: E501
            else:
                reason_str = "DENIED_BY_POLICY: Strict policy enforcement."
            final_decision = "DENIED"
        elif winner.decision == "REQUIRE_APPROVAL":
            if "ALLOW" in distinct_decisions:
                reason_str = "REQUIRE_APPROVAL_OVERRIDES_ALLOW: Human approval requirement takes precedence over ALLOW."  # noqa: E501
            else:
                reason_str = "REQUIRE_APPROVAL_BY_POLICY: Policy rule requires human approval."
            final_decision = "REQUIRE_APPROVAL"
        else:
            reason_str = "ALLOW_ALL_PASSED: All applicable policy rules passed successfully."
            final_decision = "ALLOW"

        return PolicyConflictResolutionResult(
            decision=final_decision,
            winning_policy_id=winner.policy_id,
            winning_rule_id=winner.rule_id,
            conflicting_policy_ids=conflicting_ids,
            conflict_detected=conflict_detected,
            resolution_reason=reason_str,
            evaluated_at=now,
        )
