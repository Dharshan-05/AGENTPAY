"""Pydantic Transport & Domain Schemas for Model Serialization (Phase 243)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class SerializedArtifactManifest(BaseModel):
    """Immutable metadata manifest describing a serialized XGBoost model artifact (Phase 243)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    model_id: str = Field(..., description="Unique model identity identifier")
    model_version: str = Field(..., description="Semantic version tag (e.g. 1.0.0)")
    model_family: str = Field(default="XGBoost", description="Model family framework")
    format: str = Field(default="json", description="Serialization format (json, ubjson)")
    feature_names: list[str] = Field(..., description="Ordered bound feature names")
    feature_versions: dict[str, str] = Field(..., description="Locked feature versions map")
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    training_run_id: uuid.UUID = Field(..., description="Source training run UUID")
    optimization_run_id: uuid.UUID | None = Field(
        default=None, description="Source optimization run UUID"
    )
    evaluation_id: uuid.UUID | None = Field(
        default=None, description="Associated evaluation run UUID"
    )
    configuration_hash: str = Field(..., description="SHA-256 training config hash")
    serializer_version: str = Field(default="1.0.0", description="ModelSerializer engine version")
    checksum: str = Field(
        ..., description="SHA-256 cryptographic checksum over exact raw artifact bytes"
    )
    artifact_size_bytes: int = Field(..., ge=0, description="Exact size of artifact in bytes")
    serialized_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Serialization timestamp UTC",
    )
