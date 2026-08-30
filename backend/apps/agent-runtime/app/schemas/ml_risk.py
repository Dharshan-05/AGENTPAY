"""Pydantic Transport & Domain Schemas for FraudGuard Risk Scoring Layer (Phases 249-255)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class FraudProbabilityResult(BaseModel):
    """Validated Fraud Probability domain result (Phase 249)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    inference_id: uuid.UUID = Field(..., description="Source inference run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Requesting agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    model_id: str = Field(..., description="Registered model ID")
    model_version: str = Field(..., description="Registered model SemVer string")
    fraud_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Raw model fraud probability [0.0, 1.0]"
    )
    probability_version: str = Field(default="1.0.0", description="Probability contract version")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Generation timestamp UTC"
    )
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    source_fingerprint: str = Field(..., description="SHA-256 source request fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class TransactionRiskScoreConfig(BaseModel):
    """Immutable Configuration Contract for Transaction Risk Scoring (Phase 250)."""

    model_config = ConfigDict(extra="forbid")

    score_version: str = Field(default="1.0.0", description="Score engine version")
    minimum_probability: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Min probability boundary"
    )
    maximum_probability: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Max probability boundary"
    )
    score_min: float = Field(default=0.0, ge=0.0, le=100.0, description="Min score boundary")
    score_max: float = Field(default=100.0, ge=0.0, le=100.0, description="Max score boundary")
    transformation_method: str = Field(default="LINEAR_SCALED", description="Score mapping method")
    low_threshold: float = Field(default=25.0, description="Threshold for LOW risk band")
    medium_threshold: float = Field(default=50.0, description="Threshold for MEDIUM risk band")
    high_threshold: float = Field(default=75.0, description="Threshold for HIGH risk band")
    configuration_version: str = Field(default="1.0.0", description="Config version")


class TransactionRiskResult(BaseModel):
    """Governed Transaction Risk Score Result (Phase 250)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Requesting agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    fraud_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Fraud probability [0.0, 1.0]"
    )
    transaction_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Transaction risk score [0.0, 100.0]"
    )
    risk_level: str = Field(..., description="Risk level band (LOW, MEDIUM, HIGH, CRITICAL)")
    score_version: str = Field(default="1.0.0", description="Score engine version")
    threshold_version: str = Field(default="1.0.0", description="Threshold version")
    source_inference_id: uuid.UUID = Field(..., description="Source inference run UUID")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Generation timestamp UTC"
    )


class MLBehaviourRiskResult(BaseModel):
    """Governed Behaviour Risk Score Result (Phase 251)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    behaviour_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Normalized behaviour risk score [0.0, 100.0]"
    )
    behaviour_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Behaviour confidence score [0.0, 1.0]"
    )
    is_cold_start: bool = Field(default=False, description="Whether agent is in cold start state")
    source_scale: str = Field(default="[0,100]", description="Upstream source scale")
    target_scale: str = Field(default="[0,100]", description="Target scale")
    transformation_version: str = Field(
        default="1.0.0", description="Transformation version string"
    )
    signal_timestamp: datetime = Field(..., description="Upstream signal timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class MerchantRiskResult(BaseModel):
    """Governed Merchant Risk Intelligence Result (Phase 252)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    merchant_id: str | None = Field(default=None, description="Merchant identifier")
    merchant_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Merchant risk score [0.0, 100.0]"
    )
    merchant_familiarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Familiarity score [0.0, 1.0]"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Merchant confidence score [0.0, 1.0]"
    )
    is_new_merchant: bool = Field(default=False, description="Whether merchant is new to agent")
    is_cold_start: bool = Field(default=False, description="Whether merchant has cold-start status")  # noqa: E501
    source: str = Field(
        default="AGENTGUARD_MERCHANT_ANALYSIS", description="Upstream signal source"
    )
    signal_timestamp: datetime = Field(..., description="Signal evaluation timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    source_fingerprint: str = Field(..., description="SHA-256 source fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class VelocityRiskResult(BaseModel):
    """Governed Velocity Risk Intelligence Result (Phase 253)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    velocity_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Velocity risk score [0.0, 100.0]"
    )
    burst_detected: bool = Field(default=False, description="Velocity burst flag")
    transaction_count: int = Field(default=0, ge=0, description="Window transaction count")
    amount_velocity: float = Field(default=0.0, ge=0.0, description="Window monetary sum float")
    time_window: str = Field(default="1h", description="Velocity window tag")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Velocity confidence score [0.0, 1.0]"
    )
    source: str = Field(
        default="AGENTGUARD_VELOCITY_ENGINE", description="Upstream velocity source"
    )
    signal_timestamp: datetime = Field(..., description="Signal evaluation timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    source_fingerprint: str = Field(..., description="SHA-256 source fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class IntentRiskResult(BaseModel):
    """Governed Intent Risk Intelligence Result (Phase 254)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    intent_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Intent risk score [0.0, 100.0]"
    )
    intent_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Intent confidence score [0.0, 1.0]"
    )
    intent_can_proceed: bool = Field(default=True, description="Intent engine recommendation flag")
    intent_decision: str = Field(default="VERIFIED", description="Intent verification decision")
    is_available: bool = Field(default=True, description="Whether intent signal was available")
    source: str = Field(default="AGENTGUARD_INTENT_ENGINE", description="Upstream intent source")
    signal_timestamp: datetime = Field(..., description="Signal timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    source_fingerprint: str = Field(..., description="SHA-256 source fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class PolicyRiskResult(BaseModel):
    """Governed Policy Risk Intelligence Result (Phase 255)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    policy_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Policy risk score [0.0, 100.0]"
    )
    policy_decision: str = Field(
        ..., description="Policy decision (ALLOW, DENY, REQUIRE_APPROVAL, NO_APPLICABLE_POLICY)"
    )
    policy_decision_code: str = Field(..., description="Structured decision code")
    policy_reason_count: int = Field(default=0, ge=0, description="Reason code count")
    authoritative: bool = Field(default=True, description="Policy decision authority flag")
    ml_advisory: bool = Field(default=True, description="ML advisory precedence flag")
    allow_ml_scoring: bool = Field(
        default=True, description="False if policy DENY forbids downstream ML authorization"
    )
    source: str = Field(default="AGENTGUARD_POLICY_ENGINE", description="Upstream policy source")
    signal_timestamp: datetime = Field(..., description="Policy evaluation timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    source_fingerprint: str = Field(..., description="SHA-256 source fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
