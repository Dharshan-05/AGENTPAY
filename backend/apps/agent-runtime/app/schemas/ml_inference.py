"""Pydantic Transport & Domain Schemas for FraudGuard Inference Engine (Phases 246-248)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InferenceRequest(BaseModel):
    """Payload request for FraudGuard ML model inference (Phase 246)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Requesting agent UUID")
    transaction_id: str = Field(..., description="Target transaction or request identifier")
    prediction_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Point-in-time timestamp for prediction UTC",
    )
    model_name: str = Field(default="fraudguard_xgboost", description="Target model name")
    feature_values: dict[str, Any] = Field(..., description="Raw feature key-value map")
    feature_timestamps: dict[str, datetime] = Field(
        default_factory=dict, description="Point-in-time timestamps for individual features UTC"
    )
    required_feature_versions: dict[str, str] = Field(
        default_factory=dict, description="Locked required feature versions map"
    )


class InferenceResult(BaseModel):
    """Structured result outcome of FraudGuard model inference execution (Phase 246)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    inference_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Inference run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Requesting agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    model_id: str = Field(..., description="Registered model ID")
    model_version: str = Field(..., description="Registered model SemVer string")
    feature_versions: dict[str, str] = Field(..., description="Feature versions map")
    prediction_timestamp: datetime = Field(
        ..., description="Point-in-time prediction timestamp UTC"
    )  # noqa: E501
    fraud_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Fraud probability [0.0, 1.0]"
    )  # noqa: E501
    inference_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Inference execution timestamp UTC"
    )
    configuration_hash: str = Field(..., description="SHA-256 configuration fingerprint hash")
    request_fingerprint: str = Field(..., description="SHA-256 canonical request fingerprint hash")
    status: str = Field(default="SUCCEEDED", description="Inference status")


class InferenceManifest(BaseModel):
    """Immutable audit manifest logging a FraudGuard inference execution (Phase 246.18)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    inference_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Inference run UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Requesting agent UUID")
    transaction_id: str = Field(..., description="Target transaction identifier")
    model_version: str = Field(..., description="Model SemVer string")
    artifact_checksum: str = Field(..., description="Model artifact SHA-256 checksum")
    feature_versions: dict[str, str] = Field(..., description="Feature versions map")
    preprocessing_version: str = Field(default="2.0", description="DataPreprocessor state version")
    transformation_version: str = Field(
        default="1.0.0", description="FeatureTransformation version"
    )  # noqa: E501
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    inference_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Inference timestamp UTC"
    )
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted fraud probability")  # noqa: E501
    configuration_hash: str = Field(..., description="SHA-256 configuration hash")
    request_fingerprint: str = Field(..., description="Canonical request fingerprint hash")
    result_fingerprint: str = Field(..., description="Canonical result fingerprint hash")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Manifest creation timestamp UTC"
    )
