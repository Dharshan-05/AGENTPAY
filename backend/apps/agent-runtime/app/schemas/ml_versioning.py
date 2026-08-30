"""Pydantic Transport & Domain Schemas for Model Versioning (Phase 244)."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelLifecycleState:
    """Allowed lifecycle states for ML Model Versions (Phase 244)."""

    DRAFT = "DRAFT"
    TRAINED = "TRAINED"
    EVALUATED = "EVALUATED"
    VALIDATED = "VALIDATED"
    REGISTERED = "REGISTERED"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"

    ALL_STATES = {
        DRAFT,
        TRAINED,
        EVALUATED,
        VALIDATED,
        REGISTERED,
        STAGING,
        PRODUCTION,
        DEPRECATED,
        RETIRED,
    }


VALID_STATE_TRANSITIONS: dict[str, set[str]] = {
    ModelLifecycleState.DRAFT: {ModelLifecycleState.TRAINED},
    ModelLifecycleState.TRAINED: {ModelLifecycleState.EVALUATED},
    ModelLifecycleState.EVALUATED: {ModelLifecycleState.VALIDATED},
    ModelLifecycleState.VALIDATED: {ModelLifecycleState.REGISTERED},
    ModelLifecycleState.REGISTERED: {
        ModelLifecycleState.STAGING,
        ModelLifecycleState.PRODUCTION,
        ModelLifecycleState.DEPRECATED,
    },
    ModelLifecycleState.STAGING: {
        ModelLifecycleState.PRODUCTION,
        ModelLifecycleState.DEPRECATED,
    },
    ModelLifecycleState.PRODUCTION: {
        ModelLifecycleState.DEPRECATED,
        ModelLifecycleState.RETIRED,
    },
    ModelLifecycleState.DEPRECATED: {
        ModelLifecycleState.RETIRED,
        ModelLifecycleState.STAGING,
        ModelLifecycleState.PRODUCTION,
    },
    ModelLifecycleState.RETIRED: set(),  # Terminal state! Cannot transition out of RETIRED!
}


class ModelVersionRecord(BaseModel):
    """Immutable Model Version domain record with lifecycle tracking (Phase 244)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    model_id: str = Field(..., description="Model identifier tag (e.g. fraudguard_xgb)")
    model_version: str = Field(
        ..., description="Semantic version tag MAJOR.MINOR.PATCH (e.g. 1.0.0)"
    )  # noqa: E501
    model_name: str = Field(default="fraudguard_xgboost", description="Human readable model name")
    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    model_family: str = Field(default="XGBoost", description="Framework family type")
    lifecycle_state: str = Field(
        default=ModelLifecycleState.REGISTERED, description="Current lifecycle state"
    )
    artifact_checksum: str = Field(..., description="SHA-256 artifact checksum")
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    feature_versions: dict[str, str] = Field(..., description="Locked feature versions map")
    training_run_id: uuid.UUID = Field(..., description="Source training run UUID")
    optimization_run_id: uuid.UUID | None = Field(
        default=None, description="Source optimization run UUID"
    )  # noqa: E501
    evaluation_id: uuid.UUID | None = Field(default=None, description="Associated evaluation UUID")
    configuration_hash: str = Field(..., description="SHA-256 training config hash")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Record creation timestamp UTC"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last state change timestamp UTC"
    )

    @field_validator("model_version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        """Validate Semantic Versioning pattern MAJOR.MINOR.PATCH."""
        pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(pattern, v):
            raise ValueError(
                f"model_version '{v}' must satisfy SemVer pattern MAJOR.MINOR.PATCH (e.g. 1.0.0)"
            )  # noqa: E501
        return v

    @field_validator("lifecycle_state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate lifecycle state presence in allowed set."""
        if v not in ModelLifecycleState.ALL_STATES:
            raise ValueError(
                f"Invalid lifecycle state '{v}'. Must be one of {ModelLifecycleState.ALL_STATES}"
            )  # noqa: E501
        return v
