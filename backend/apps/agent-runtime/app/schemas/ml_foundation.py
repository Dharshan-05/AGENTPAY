"""Pydantic Transport & Domain Schemas for ML Data Pipeline Foundation (Phases 216-218)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PipelineReproducibilityManifest(BaseModel):
    """Manifest tracking exact inputs and code versions for pipeline execution (Phase 216)."""

    model_config = ConfigDict(extra="forbid")

    manifest_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Manifest UUID")
    pipeline_version: str = Field(..., description="Pipeline version")
    dataset_version: str = Field(..., description="Dataset version")
    schema_version: str = Field(..., description="Schema version")
    feature_version: str = Field(..., description="Feature pipeline version")
    preprocessing_version: str = Field(..., description="Preprocessing version")
    code_version: str = Field(default="git-sha-latest", description="Code commit hash")
    configuration_hash: str = Field(..., description="SHA-256 hash of configuration")
    dependency_snapshot: dict[str, str] = Field(
        default_factory=dict, description="Snapshot of key package dependencies"
    )
    random_seed: int = Field(default=42, description="Random seed used")
    execution_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Manifest generation timestamp"
    )


class PipelineExecutionRecord(BaseModel):
    """Pipeline execution identity and status tracking record (Phase 216)."""

    model_config = ConfigDict(extra="forbid")

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Execution UUID")
    run_id: str = Field(..., description="Run identifier string")
    pipeline_version: str = Field(..., description="Pipeline version")
    status: str = Field(
        default="PENDING",
        description="Execution status (PENDING, RUNNING, SUCCEEDED, FAILED, CANCELLED)",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Start timestamp UTC"
    )
    completed_at: datetime | None = Field(default=None, description="Completion timestamp UTC")


class DatasetContract(BaseModel):
    """Formal contract describing dataset specification (Phase 217)."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Dataset UUID")
    dataset_version: str = Field(..., description="Dataset semantic version")
    schema_version: str = Field(..., description="Schema version")
    source: str = Field(..., description="Data source origin")
    owner: str = Field(default="fraudguard-team", description="Dataset owner team/user")
    description: str = Field(default="", description="Dataset documentation")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )
    effective_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Effective start timestamp"
    )
    effective_to: datetime | None = Field(default=None, description="Effective end timestamp")


class DatasetSnapshot(BaseModel):
    """Immutable snapshot record of a dataset version (Phase 217)."""

    model_config = ConfigDict(extra="forbid")

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Snapshot UUID")
    dataset_name: str = Field(..., description="Dataset identifier name")
    dataset_version: str = Field(..., description="Immutable dataset version tag")
    fingerprint: str = Field(..., description="Deterministic content fingerprint hash")
    record_count: int = Field(..., ge=0, description="Captured record count")
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Snapshot capture timestamp"
    )


class DatasetMetadata(BaseModel):
    """Metadata describing ingested dataset (Phase 217)."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Dataset UUID")
    tenant_id: uuid.UUID | None = Field(
        default=None, description="Tenant isolation UUID if tenant-scoped"
    )
    dataset_name: str = Field(..., description="Dataset identifier name")
    source: str = Field(..., description="Data source origin")
    version: str = Field(default="1.0.0", description="Dataset semantic version")
    record_count: int = Field(..., ge=0, description="Total ingested record count")
    schema_version: str = Field(default="1.0", description="Dataset schema version")
    fingerprint: str | None = Field(default=None, description="Dataset fingerprint hash")
    ingested_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Ingestion timestamp UTC"
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional non-sensitive dataset attributes"
    )


class DatasetValidationViolation(BaseModel):
    """Structured dataset validation violation entry (Phase 218)."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Violation category code")
    field_name: str | None = Field(default=None, description="Target field name")
    message: str = Field(..., description="Human readable violation detail")
    severity: str = Field(default="ERROR", description="Violation severity (WARNING, ERROR, FATAL)")


class DatasetValidationResult(BaseModel):
    """Structured outcome of dataset validation (Phase 218)."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(..., description="True if dataset satisfies validation constraints")
    dataset_name: str = Field(..., description="Dataset name evaluated")
    dataset_version: str = Field(..., description="Dataset version evaluated")
    schema_version: str = Field(..., description="Schema version evaluated")
    row_count: int = Field(..., ge=0, description="Total evaluated row count")
    invalid_row_count: int = Field(..., ge=0, description="Invalid row count")
    duplicate_count: int = Field(..., ge=0, description="Duplicate row count")
    quality_score: Decimal = Field(
        default=Decimal("1.00"), description="Overall dataset quality score (0.00 to 1.00)"
    )
    quality_dimensions: dict[str, Decimal] = Field(
        default_factory=dict, description="Dimensional breakdown of dataset quality"
    )
    missing_value_summary: dict[str, int] = Field(
        default_factory=dict, description="Missing count per column"
    )
    distribution_summary: dict[str, Any] = Field(
        default_factory=dict, description="Numerical/categorical distribution metrics"
    )
    violations: list[DatasetValidationViolation] = Field(
        default_factory=list, description="List of dataset violations"
    )
    validation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Validation timestamp UTC"
    )
