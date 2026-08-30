"""Pydantic Transport & Domain Schemas for Intent Mismatch Detection Engine (Phase 199)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.intent_matching import IntentMatchResult


class IntentMismatchDetectionRequest(BaseModel):
    """Payload contract for intent mismatch detection (Phase 199)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    match_result: IntentMatchResult = Field(
        ..., description="Intent matching result from Phase 198"
    )


class IntentMismatchDetectionResult(BaseModel):
    """Structured outcome of intent mismatch detection engine (Phase 199)."""

    model_config = ConfigDict(extra="forbid")

    mismatch_detected: bool = Field(
        ..., description="True if any security-relevant mismatch was detected"
    )
    severity: str = Field(
        ..., description="Highest mismatch severity (LOW, MEDIUM, HIGH, CRITICAL, NONE)"
    )
    reason_codes: list[str] = Field(
        default_factory=list, description="Taxonomy of detected mismatch reason codes"
    )
    can_proceed: bool = Field(
        ..., description="False if mismatch requires halting policy execution (fail-closed)"
    )
    explanation: str = Field(..., description="Human-readable mismatch summary")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Detection completion timestamp"
    )
