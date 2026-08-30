"""Pydantic Transport & Domain Schemas for Policy Conflict Resolution Engine (Phase 195)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class PolicyCandidate(BaseModel):
    """Candidate policy decision outcome representation for conflict resolution (Phase 195)."""

    model_config = ConfigDict(extra="forbid")

    policy_id: uuid.UUID = Field(..., description="Security policy UUID")
    rule_id: uuid.UUID | None = Field(
        default=None, description="Optional matched rule UUID within policy"
    )
    decision: str = Field(
        ..., description="Candidate decision outcome (DENY, REQUIRE_APPROVAL, ALLOW)"
    )
    priority: int = Field(default=100, description="Policy priority integer (higher = stronger)")
    specificity: int = Field(
        default=1,
        description="Specificity rank integer (3=merchant, 2=category, 1=global)",
    )
    reason_code: str = Field(..., description="Decision reason code")


class PolicyConflictResolutionResult(BaseModel):
    """Structured outcome of resolving policy conflicts (Phase 195)."""

    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        ...,
        description="Final resolved decision outcome (DENY, REQUIRE_APPROVAL, ALLOW, NO_APPLICABLE_POLICY)",  # noqa: E501
    )
    winning_policy_id: uuid.UUID | None = Field(
        default=None, description="UUID of winning security policy"
    )
    winning_rule_id: uuid.UUID | None = Field(
        default=None, description="UUID of winning rule if applicable"
    )
    conflicting_policy_ids: list[uuid.UUID] = Field(
        default_factory=list, description="List of all policy UUIDs that competed"
    )
    conflict_detected: bool = Field(
        ..., description="True if multiple competing decisions were present"
    )
    resolution_reason: str = Field(
        ..., description="Explanation of resolution rule applied (e.g. DENY_OVERRIDES_ALLOW)"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Resolution completion timestamp"
    )
