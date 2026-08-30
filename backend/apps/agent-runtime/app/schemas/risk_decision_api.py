"""Pydantic Transport & API Schemas for Risk Decision API (Phase 284)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.risk_engine import (
    DecisionAuditEvent,
    DecisionExplanationResult,
    FinalRiskDecision,
    RiskSignal,
    RiskThresholdBand,
)

PROHIBITED_METADATA_KEYS = {
    "is_fraud",
    "fraud_label",
    "post_outcome",
    "chargeback_result",
    "investigation_result",
    "future_outcome",
}

PROHIBITED_FORGED_FIELDS = {
    "final_decision",
    "decision",
    "risk_score",
    "risk_band",
    "score",
    "override",
}


class RiskDecisionEvaluateRequest(BaseModel):
    """API Request Schema for evaluating risk decision (Phase 284)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    agent_id: uuid.UUID = Field(..., description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    prediction_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Point-in-time prediction timestamp UTC",
    )
    signals: list[RiskSignal] = Field(
        ..., min_length=1, description="List of normalized risk signals to evaluate"
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary context metadata payload"
    )

    @field_validator("context_metadata", "signals")
    @classmethod
    def validate_no_target_leakage_or_forged_decision(cls, value: Any) -> Any:
        """Reject client-supplied forged decisions, scores, or target leakage metadata."""
        if isinstance(value, dict):
            for k in value:
                if k.lower() in PROHIBITED_METADATA_KEYS:
                    raise ValueError(f"Target leakage field '{k}' is prohibited in API request.")
                if k.lower() in PROHIBITED_FORGED_FIELDS:
                    raise ValueError(
                        f"Client-supplied decision or score parameter '{k}' is prohibited."
                    )
        return value


class RiskDecisionEvaluateResponse(BaseModel):
    """API Response Schema for risk decision evaluation (Phase 284)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    decision_id: uuid.UUID = Field(..., description="Decision run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")

    decision: FinalRiskDecision = Field(
        ..., description="Authoritative final risk decision (ALLOW, REVIEW, BLOCK)"
    )
    reason_code: str = Field(..., description="Primary reason code")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Evaluated composite risk score")
    risk_band: RiskThresholdBand = Field(..., description="Matched risk threshold band")

    policy_precedence: str = Field(..., description="Preserved policy precedence string")
    hard_security_status: str = Field(..., description="Overall hard security status summary")
    cold_start: bool = Field(..., description="Cold start indicator flag")
    unavailable_signal_types: list[str] = Field(..., description="List of unavailable signal types")

    explanation: DecisionExplanationResult = Field(..., description="Detailed explanation result")
    audit_event: DecisionAuditEvent = Field(..., description="Append-only audit event record")

    decision_fingerprint: str = Field(..., description="SHA-256 decision fingerprint")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="API evaluation timestamp UTC"
    )
