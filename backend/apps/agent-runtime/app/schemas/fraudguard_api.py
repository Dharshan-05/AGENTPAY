"""Pydantic Transport & Domain Schemas for FraudGuard API (Phases 261-265)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ml_risk import (
    IntentRiskResult,
    MerchantRiskResult,
    MLBehaviourRiskResult,
    PolicyRiskResult,
    VelocityRiskResult,
)
from app.schemas.ml_xai import (
    LocalTransactionExplanation,
    RiskFactor,
)


class FraudGuardLocalXAIRequest(BaseModel):
    """API Request payload for Local Transaction XAI Explanation (Phase 261)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    model_version: str | None = Field(default=None, description="Optional explicit model version")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    feature_names: list[str] = Field(..., description="Ordered feature names")
    feature_values: list[float] = Field(..., description="Ordered feature values")
    top_k: int = Field(default=5, ge=1, le=50, description="Top factor limit")


class FraudGuardGlobalXAIRequest(BaseModel):
    """API Request payload for Global Model XAI Explanation (Phase 261)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    model_version: str = Field(..., description="Explicit registered model version")
    feature_names: list[str] = Field(..., description="Ordered feature names")
    sample_features: list[list[float]] = Field(
        ..., description="2D feature matrix (samples x features)"
    )
    dataset_fingerprint: str = Field(..., description="SHA-256 dataset fingerprint")


class FraudGuardInferenceRequest(BaseModel):
    """API Request payload for Real-Time FraudGuard Inference (Phase 263)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    model_version: str | None = Field(default=None, description="Optional explicit model version")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    feature_names: list[str] = Field(..., description="Ordered feature names")
    feature_values: list[float] = Field(..., description="Ordered feature values")
    feature_timestamps: dict[str, datetime] | None = Field(
        default=None, description="Optional per-feature timestamps map"
    )
    feature_versions: dict[str, str] | None = Field(
        default=None, description="Optional feature versions map"
    )


class FraudGuardInferenceResponse(BaseModel):
    """API Response payload for Real-Time FraudGuard Inference (Phase 263)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    inference_id: uuid.UUID = Field(..., description="Inference run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    model_name: str = Field(..., description="Target model name")
    model_version: str = Field(..., description="Model SemVer string")
    fraud_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Fraud probability [0.0, 1.0]"
    )
    artifact_checksum: str = Field(..., description="SHA-256 artifact checksum")
    request_fingerprint: str = Field(..., description="SHA-256 request fingerprint")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")


class FraudGuardRiskIntelligenceRequest(BaseModel):
    """API Request payload for FraudGuard Risk Intelligence Pipeline (Phase 264)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    model_version: str | None = Field(default=None, description="Optional explicit model version")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    feature_names: list[str] = Field(..., description="Ordered feature names")
    feature_values: list[float] = Field(..., description="Ordered feature values")
    merchant_signal: dict[str, Any] | None = Field(default=None, description="Merchant signal")
    velocity_signal: dict[str, Any] | None = Field(default=None, description="Velocity signal")
    intent_signal: dict[str, Any] | None = Field(default=None, description="Intent signal")
    policy_signal: dict[str, Any] | None = Field(default=None, description="Policy signal")


class FraudGuardRiskIntelligenceResponse(BaseModel):
    """API Response payload for FraudGuard Risk Intelligence Pipeline (Phase 264)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    risk_signal_id: uuid.UUID = Field(..., description="Risk signal UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    fraud_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Fraud probability [0.0, 1.0]"
    )
    transaction_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Transaction risk score [0.0, 100.0]"
    )
    risk_level: str = Field(..., description="Risk level band (LOW, MEDIUM, HIGH, CRITICAL)")
    behaviour_risk: MLBehaviourRiskResult | None = Field(
        default=None, description="Behaviour risk result"
    )
    merchant_risk: MerchantRiskResult | None = Field(
        default=None, description="Merchant risk result"
    )
    velocity_risk: VelocityRiskResult | None = Field(
        default=None, description="Velocity risk result"
    )
    intent_risk: IntentRiskResult | None = Field(default=None, description="Intent risk result")
    policy_risk: PolicyRiskResult | None = Field(default=None, description="Policy risk result")
    extracted_factors: list[RiskFactor] = Field(..., description="Extracted risk factors")
    policy_decision: str = Field(
        default="ALLOW", description="Authoritative policy decision string"
    )
    authoritative: bool = Field(default=True, description="Policy decision authority flag")
    ml_advisory: bool = Field(default=True, description="ML advisory status flag")
    allow_ml_scoring: bool = Field(
        default=True, description="False if policy DENY forbids downstream ML authorization"
    )
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp UTC"
    )


class FraudGuardEvaluateRequest(BaseModel):
    """API Request payload for End-to-End FraudGuard Integration (Phase 265)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    feature_names: list[str] = Field(..., description="Ordered feature names")
    feature_values: list[float] = Field(..., description="Ordered feature values")
    merchant_signal: dict[str, Any] | None = Field(default=None, description="Merchant signal")
    velocity_signal: dict[str, Any] | None = Field(default=None, description="Velocity signal")
    intent_signal: dict[str, Any] | None = Field(default=None, description="Intent signal")
    policy_signal: dict[str, Any] | None = Field(default=None, description="Policy signal")
    include_xai: bool = Field(default=True, description="Whether to include local XAI explanation")
    top_k: int = Field(default=5, ge=1, le=50, description="Top factor limit for XAI")


class FraudGuardEvaluateResponse(BaseModel):
    """API Response payload for End-to-End FraudGuard Integration (Phase 265)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    authoritative_decision: str = Field(
        ..., description="Authoritative decision (ALLOW, DENY, REQUIRE_APPROVAL)"
    )
    authoritative_source: str = Field(default="POLICY_ENGINE", description="Decision source engine")
    allow_ml_scoring: bool = Field(
        ..., description="False if policy DENY forbids downstream ML authorization"
    )
    advisory_risk_intelligence: FraudGuardRiskIntelligenceResponse = Field(
        ..., description="Advisory risk intelligence pipeline payload"
    )
    local_explanation: LocalTransactionExplanation | None = Field(
        default=None, description="Optional local XAI explanation"
    )
    audit_manifest: dict[str, Any] = Field(..., description="Comprehensive audit manifest")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp UTC"
    )
