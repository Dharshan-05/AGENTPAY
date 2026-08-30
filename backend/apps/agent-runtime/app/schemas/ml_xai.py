"""Pydantic Transport & Domain Schemas for FraudGuard Explainable AI (Phases 256-260)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

PROHIBITED_LEAKAGE_FEATURES = {
    "is_fraud",
    "fraud_label",
    "post_outcome",
    "investigation_result",
    "chargeback_result",
    "future_outcome",
}


class ShapConfig(BaseModel):
    """Immutable Configuration Contract for SHAP Explainer (Phase 256)."""

    model_config = ConfigDict(extra="forbid")

    explainer_type: str = Field(default="TreeExplainer", description="SHAP explainer engine type")
    output_space: str = Field(default="MARGIN", description="Output space (MARGIN or PROBABILITY)")
    top_k: int = Field(default=5, ge=1, le=50, description="Top factor limit for local summary")
    prohibited_features: list[str] = Field(
        default_factory=lambda: sorted(list(PROHIBITED_LEAKAGE_FEATURES)),
        description="List of forbidden target leakage features",
    )
    configuration_version: str = Field(default="1.0.0", description="Config version tag")


class ShapAttributionResult(BaseModel):
    """Immutable SHAP Feature Attribution Result (Phase 256)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    explanation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Explanation run UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str | None = Field(default=None, description="Target transaction ID")
    model_name: str = Field(..., description="Target model name")
    model_version: str = Field(..., description="Target model SemVer string")
    artifact_checksum: str = Field(..., description="SHA-256 artifact checksum")
    feature_names: list[str] = Field(..., description="Ordered bound feature names")
    feature_versions: dict[str, str] = Field(..., description="Locked feature versions map")
    shap_values: list[float] = Field(..., description="SHAP attribution values (1-to-1 ordered)")
    base_value: float = Field(..., description="SHAP explainer expected base value")
    prediction_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Model prediction probability"
    )
    output_space: str = Field(
        default="MARGIN", description="SHAP output space (MARGIN/PROBABILITY)"
    )  # noqa: E501
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Attribution timestamp UTC"
    )


class ShapFeatureImportance(BaseModel):
    """Normalized SHAP Feature Importance Detail (Phase 257)."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str = Field(..., description="Feature name identifier")
    feature_version: str = Field(default="1.0.0", description="Feature version string")
    shap_value: float = Field(..., description="Raw SHAP attribution value")
    absolute_importance: float = Field(..., ge=0.0, description="Absolute SHAP magnitude |shap|")
    relative_importance: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized relative importance [0.0, 1.0]"
    )
    direction: str = Field(..., description="Attribution direction (POSITIVE, NEGATIVE, NEUTRAL)")
    rank: int = Field(..., ge=1, description="Importance rank index")


class LocalTransactionExplanation(BaseModel):
    """Governed Local Transaction Explanation (Phase 258)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    explanation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Explanation run UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    model_name: str = Field(..., description="Target model name")
    model_version: str = Field(..., description="Target model SemVer string")
    artifact_checksum: str = Field(..., description="SHA-256 artifact checksum")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted fraud probability")
    transaction_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Transaction risk score"
    )
    risk_level: str = Field(..., description="Risk level band (LOW, MEDIUM, HIGH, CRITICAL)")
    top_positive_factors: list[ShapFeatureImportance] = Field(
        ..., description="Top features contributing positively to risk"
    )
    top_negative_factors: list[ShapFeatureImportance] = Field(
        ..., description="Top features contributing negatively to risk"
    )
    all_feature_importance: list[ShapFeatureImportance] = Field(
        ..., description="Complete ordered feature importance list"
    )
    shap_base_value: float = Field(..., description="SHAP base value")
    output_space: str = Field(default="MARGIN", description="SHAP output space")
    explanation_statement: str = Field(
        ..., description="Non-causal, structured explanation text statement"
    )
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    explanation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Explanation timestamp UTC"
    )
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")


class GlobalFeatureImportance(BaseModel):
    """Aggregate Global Model Feature Importance Detail (Phase 259)."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str = Field(..., description="Feature name identifier")
    feature_version: str = Field(default="1.0.0", description="Feature version string")
    mean_absolute_shap: float = Field(
        ..., ge=0.0, description="Mean absolute SHAP value across dataset"
    )
    relative_importance: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized global relative importance [0.0, 1.0]"
    )
    rank: int = Field(..., ge=1, description="Deterministic rank index")


class GlobalModelExplanation(BaseModel):
    """Governed Global Model Explanation (Phase 259)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    explanation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Explanation run UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    model_name: str = Field(..., description="Target model name")
    model_version: str = Field(..., description="Target model SemVer string")
    artifact_checksum: str = Field(..., description="SHA-256 artifact checksum")
    dataset_fingerprint: str = Field(..., description="Analyzed dataset fingerprint")
    feature_versions: dict[str, str] = Field(..., description="Feature versions map")
    sample_count: int = Field(..., ge=1, description="Sample count analyzed")
    feature_count: int = Field(..., ge=1, description="Feature count analyzed")
    feature_importance: list[GlobalFeatureImportance] = Field(
        ..., description="Complete deterministically ranked feature importance list"
    )
    explanation_statement: str = Field(..., description="Non-causal global model summary text")
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )


class RiskFactorConfig(BaseModel):
    """Immutable Configuration Contract for Risk Factor Extraction (Phase 260)."""

    model_config = ConfigDict(extra="forbid")

    low_threshold: float = Field(default=25.0, description="Threshold for LOW severity factor")
    medium_threshold: float = Field(
        default=50.0, description="Threshold for MEDIUM severity factor"
    )
    high_threshold: float = Field(default=75.0, description="Threshold for HIGH severity factor")
    critical_threshold: float = Field(
        default=90.0, description="Threshold for CRITICAL severity factor"
    )
    config_version: str = Field(default="1.0.0", description="Config version tag")


class RiskFactor(BaseModel):
    """Structured Explainable Risk Factor (Phase 260)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    factor_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Risk factor UUID")
    factor_type: str = Field(
        ...,
        description="Factor category (MODEL_FEATURE, BEHAVIOUR, MERCHANT, VELOCITY, INTENT, POLICY)",  # noqa: E501
    )
    feature_name: str | None = Field(default=None, description="Feature name if applicable")
    feature_version: str | None = Field(default=None, description="Feature version if applicable")
    source: str = Field(..., description="Upstream signal source system")
    value: float = Field(..., description="Raw signal numerical value")
    unit: str = Field(default="[0,100]", description="Value scale unit ([0,1], [0,100], COUNT)")
    direction: str = Field(default="NEUTRAL", description="Direction (POSITIVE, NEGATIVE, NEUTRAL)")  # noqa: E501
    severity: str = Field(
        default="LOW", description="Factor severity (LOW, MEDIUM, HIGH, CRITICAL)"
    )
    shap_value: float | None = Field(
        default=None, description="Associated SHAP value if model feature"
    )  # noqa: E501
    relative_importance: float | None = Field(
        default=None, description="Associated relative importance"
    )
    description: str = Field(..., description="Human readable factor explanation text")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    model_version: str = Field(..., description="Associated model version string")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )


class RiskFactorExtractionResult(BaseModel):
    """Governed Risk Factor Extraction Manifest (Phase 260)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    extraction_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Extraction run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    factors: list[RiskFactor] = Field(..., description="Deduplicated structured risk factor list")
    has_policy_deny: bool = Field(
        default=False, description="Whether authoritative policy DENY exists"
    )
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )
