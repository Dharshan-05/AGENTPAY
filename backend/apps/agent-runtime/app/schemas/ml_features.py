"""Pydantic Transport & Domain Schemas for Feature Validation & Feature Store (Phases 229-230)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FeatureValidationViolation(BaseModel):
    """Violation item produced by FeatureValidator (Phase 229)."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str = Field(..., description="Feature name")
    code: str = Field(..., description="Violation error code")
    message: str = Field(..., description="Detailed violation explanation")
    severity: str = Field(default="ERROR", description="Severity (WARNING, ERROR, FATAL)")


class FeatureValidationResult(BaseModel):
    """Outcome of Feature Validation Gate (Phase 229)."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(..., description="True if feature vector satisfies quality gate")
    feature_count: int = Field(..., ge=0, description="Total count of features validated")
    quality_score: Decimal = Field(
        default=Decimal("1.00"), description="Feature set quality score (0.00 to 1.00)"
    )
    leakage_detected: bool = Field(
        default=False, description="True if target or temporal leakage is detected"
    )
    violations: list[FeatureValidationViolation] = Field(
        default_factory=list, description="List of feature violations"
    )
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Validation timestamp UTC"
    )


class FeatureLineageGraphNode(BaseModel):
    """Lineage node mapping feature provenance (Phase 230)."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str = Field(..., description="Feature name")
    source: str = Field(..., description="Source subsystem")
    dataset_version: str = Field(..., description="Upstream dataset version tag")
    dependencies: list[str] = Field(
        default_factory=list, description="Upstream feature dependencies"
    )  # noqa: E501


class FeatureStoreRecord(BaseModel):
    """Metadata record representing a feature in the Feature Store Registry (Phase 230)."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str = Field(..., description="Unique feature identifier (name:version)")
    name: str = Field(..., description="Unique feature identifier name")
    feature_type: str = Field(..., description="Data type of feature")
    category: str = Field(default="META", description="Feature category taxonomy")
    security_classification: str = Field(
        default="INTERNAL", description="Security level (PUBLIC, INTERNAL, SENSITIVE, RESTRICTED)"
    )
    source: str = Field(..., description="Origin source system")
    version: str = Field(default="1.0.0", description="Feature semantic version")
    status: str = Field(
        default="ACTIVE",
        description="Lifecycle status (DRAFT, VALIDATING, ACTIVE, DEPRECATED, RETIRED)",
    )
    description: str = Field(default="", description="Feature documentation description")
    freshness_seconds: int = Field(default=3600, description="Feature TTL / freshness seconds")
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Registration timestamp UTC"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last status update timestamp"
    )
    attributes: dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
