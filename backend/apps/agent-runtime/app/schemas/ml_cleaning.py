"""Pydantic Transport & Domain Schemas for Data Cleaning & Preprocessing (Phases 219-220)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CleaningRuleAudit(BaseModel):
    """Audit entry recording a specific cleaning rule execution (Phase 219)."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(..., description="Unique cleaning rule code identifier")
    category: str = Field(
        ...,
        description="Rule category (NULL_HANDLING, TYPE_NORMALIZATION, DUPLICATE_REMOVAL, RANGE_VALIDATION, TIMESTAMP_NORMALIZATION, CATEGORY_NORMALIZATION, CURRENCY_NORMALIZATION, IDENTIFIER_VALIDATION)",  # noqa: E501
    )
    input_count: int = Field(..., ge=0, description="Input record count")
    output_count: int = Field(..., ge=0, description="Output record count")
    modified_count: int = Field(..., ge=0, description="Modified record count")
    removed_count: int = Field(..., ge=0, description="Removed record count")
    reason: str = Field(..., description="Explanation of rule application")


class QuarantineRecord(BaseModel):
    """Forensic record storing quarantined invalid data without sensitive raw value exposure (Phase 219)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid")

    quarantine_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Quarantine UUID")
    reason_code: str = Field(..., description="Rejection reason code")
    raw_data_hash: str = Field(..., description="SHA-256 hash of quarantined record")
    field_summary: dict[str, str] = Field(
        default_factory=dict, description="Non-sensitive metadata of rejected fields"
    )
    quarantined_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Quarantine timestamp UTC"
    )


class DataCleaningResult(BaseModel):
    """Structured statistical outcome of data cleaning pipeline (Phase 219)."""

    model_config = ConfigDict(extra="forbid")

    input_rows: int = Field(..., ge=0, description="Total input row count")
    clean_rows: int = Field(..., ge=0, description="Cleaned output row count")
    removed_rows: int = Field(..., ge=0, description="Total removed row count")
    modified_rows: int = Field(..., ge=0, description="Total modified row count")
    duplicate_rows: int = Field(..., ge=0, description="Duplicate row count removed")
    invalid_rows: int = Field(..., ge=0, description="Invalid row count removed")
    quarantined_rows: int = Field(default=0, ge=0, description="Quarantined row count")
    rule_audits: list[CleaningRuleAudit] = Field(
        default_factory=list, description="Audit entries for cleaning rules applied"
    )
    cleaning_version: str = Field(default="2.0", description="Cleaning pipeline version")
    cleaned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Cleaning timestamp UTC"
    )


class PreprocessorState(BaseModel):
    """Serialized state of DataPreprocessor for inference consistency (Phase 220)."""

    model_config = ConfigDict(extra="forbid")

    feature_means: dict[str, float] = Field(
        default_factory=dict, description="Mean values per numerical feature"
    )
    feature_stds: dict[str, float] = Field(
        default_factory=dict, description="Standard deviations per numerical feature"
    )
    categorical_encodings: dict[str, dict[str, int]] = Field(
        default_factory=dict, description="Categorical string to integer encodings"
    )
    imputation_defaults: dict[str, Any] = Field(
        default_factory=dict, description="Imputation default values"
    )
    is_fitted: bool = Field(default=False, description="True if preprocessor has been fitted")
    preprocessor_version: str = Field(default="2.0", description="Preprocessor version")
    fit_dataset_version: str = Field(default="1.0.0", description="Fit dataset version tag")
    configuration_hash: str = Field(default="", description="Preprocessor configuration hash")
