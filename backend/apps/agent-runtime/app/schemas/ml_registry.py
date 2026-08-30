"""Pydantic Transport & Domain Schemas for Model Registry (Phase 245)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ml_evaluation import EvaluationManifest
from app.schemas.ml_serialization import SerializedArtifactManifest


class QualityGateConfig(BaseModel):
    """Configurable threshold quality gates required for production model promotion (Phase 245)."""

    model_config = ConfigDict(extra="forbid")

    minimum_precision: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum acceptable precision score"
    )
    minimum_recall: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum acceptable recall score"
    )
    minimum_f1: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum acceptable F1 score"
    )
    minimum_roc_auc: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum acceptable ROC-AUC score"
    )
    minimum_pr_auc: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum acceptable PR-AUC score"
    )


class RegisteredModelManifest(BaseModel):
    """Immutable domain manifest for a model registered in the FraudGuard Model Registry (Phase 245)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    registration_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Registration entry UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    model_name: str = Field(..., description="Target model name identifier")
    model_version: str = Field(..., description="Semantic version string MAJOR.MINOR.PATCH")
    lifecycle_state: str = Field(
        default="REGISTERED",
        description="Lifecycle state (REGISTERED, STAGING, PRODUCTION, DEPRECATED, RETIRED)",  # noqa: E501
    )
    artifact_manifest: SerializedArtifactManifest = Field(
        ..., description="Serialized artifact metadata manifest"
    )
    evaluation_manifest: EvaluationManifest = Field(
        ..., description="Evaluation metrics metadata manifest"
    )
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Registration timestamp UTC"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last modification timestamp UTC"
    )


class RegistryAuditRecord(BaseModel):
    """Audit entry recording model registry state changes and promotions (Phase 245)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    audit_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Audit log entry UUID")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    model_name: str = Field(..., description="Model identifier name")
    model_version: str = Field(..., description="Model semver string")
    action: str = Field(..., description="Lifecycle action executed")
    previous_state: str = Field(..., description="State prior to action")
    new_state: str = Field(..., description="State resulting from action")
    actor: str = Field(default="system", description="Triggering actor context")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Audit timestamp UTC"
    )
