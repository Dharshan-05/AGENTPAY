"""Pydantic Transport & Domain Schemas for FraudGuard ML Model Training & Optimization (Phases 231-235)."""  # noqa: E501

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImbalanceAnalysisResult(BaseModel):
    """Structured report produced by ImbalanceHandler (Phase 231)."""

    model_config = ConfigDict(extra="forbid")

    total_samples: int = Field(..., ge=0, description="Total sample count")
    positive_samples: int = Field(..., ge=0, description="Fraud positive (label=1) sample count")
    negative_samples: int = Field(
        ..., ge=0, description="Legitimate negative (label=0) sample count"
    )
    positive_ratio: float = Field(..., ge=0.0, le=1.0, description="Positive class ratio")
    negative_ratio: float = Field(..., ge=0.0, le=1.0, description="Negative class ratio")
    imbalance_ratio: float = Field(..., ge=0.0, description="Ratio of negative to positive samples")
    class_counts: dict[str, int] = Field(default_factory=dict, description="Counts per label value")
    selected_strategy: str = Field(
        default="NONE",
        description="Applied strategy (NONE, CLASS_WEIGHT, RANDOM_OVERSAMPLING, RANDOM_UNDERSAMPLING, SMOTE)",  # noqa: E501
    )
    strategy_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Resampling or strategy execution parameters"
    )
    class_weights: dict[str, float] = Field(
        default_factory=dict, description="Computed class weights for model loss"
    )
    training_only: bool = Field(
        default=True, description="Enforces resampling affected training set ONLY"
    )
    random_seed: int = Field(default=42, description="Deterministic random seed used")
    warnings: list[str] = Field(default_factory=list, description="Warnings or quality flags")
    analyzed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Analysis timestamp UTC"
    )


class TrainingDatasetManifest(BaseModel):
    """Manifest describing a canonical FraudGuard training dataset (Phase 232)."""

    model_config = ConfigDict(extra="forbid")

    training_dataset_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Training dataset UUID"
    )
    dataset_version: str = Field(..., description="Dataset version tag")
    dataset_fingerprint: str = Field(..., description="Deterministic SHA-256 content fingerprint")
    feature_versions: dict[str, str] = Field(
        default_factory=dict, description="Locked feature versions map"
    )
    preprocessor_version: str = Field(default="2.0", description="Preprocessor version")
    schema_version: str = Field(default="1.0", description="Schema version")
    pipeline_version: str = Field(default="1.0.0", description="Pipeline version")
    target_definition: str = Field(default="is_fraud", description="Target label field name")
    row_count: int = Field(..., ge=0, description="Total record count")
    feature_count: int = Field(..., ge=0, description="Total feature count")
    quality_score: Decimal = Field(
        default=Decimal("1.00"), description="Training dataset quality score"
    )
    leakage_status: bool = Field(
        default=False, description="True if target or temporal leakage detected"
    )
    tenant_id: str | None = Field(default=None, description="Tenant isolation boundary")
    execution_id: uuid.UUID | None = Field(default=None, description="Pipeline execution UUID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )


class SplitManifest(BaseModel):
    """Manifest describing train/validation/test dataset partitioning (Phase 233)."""

    model_config = ConfigDict(extra="forbid")

    split_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Split run UUID")
    strategy: str = Field(..., description="Splitting strategy (TEMPORAL, STRATIFIED, RANDOM)")
    random_seed: int = Field(default=42, description="Random seed used")
    train_count: int = Field(..., ge=0, description="Train set record count")
    validation_count: int = Field(..., ge=0, description="Validation set record count")
    test_count: int = Field(..., ge=0, description="Test set record count")
    train_ratio: float = Field(..., ge=0.0, le=1.0, description="Train set ratio")
    validation_ratio: float = Field(..., ge=0.0, le=1.0, description="Validation set ratio")
    test_ratio: float = Field(..., ge=0.0, le=1.0, description="Test set ratio")
    temporal_boundaries: dict[str, str] = Field(
        default_factory=dict, description="Timestamp boundaries per split partition"
    )
    class_distributions: dict[str, dict[str, int]] = Field(
        default_factory=dict, description="Class label distributions per partition"
    )
    dataset_fingerprint: str = Field(..., description="Source dataset fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Partitioning timestamp UTC"
    )


class ModelTrainingResult(BaseModel):
    """Structured outcome of an XGBoost training execution run (Phase 234)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    training_run_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Training run UUID")
    model_type: str = Field(default="XGBoost", description="Model family type")
    algorithm: str = Field(default="XGBClassifier", description="Algorithm implementation name")
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    feature_count: int = Field(..., ge=0, description="Bound feature count")
    feature_names: list[str] = Field(..., description="Ordered bound feature names")
    feature_versions: dict[str, str] = Field(..., description="Locked feature versions")
    training_rows: int = Field(..., ge=0, description="Training dataset row count")
    validation_rows: int = Field(..., ge=0, description="Validation dataset row count")
    hyperparameters: dict[str, Any] = Field(..., description="Training hyperparameters")
    random_seed: int = Field(default=42, description="Deterministic random seed used")
    early_stopping_enabled: bool = Field(default=True, description="True if early stopping used")
    best_iteration: int | None = Field(default=None, description="Best iteration tree index")
    best_score: float | None = Field(default=None, description="Best validation evaluation score")
    training_duration_seconds: float = Field(..., ge=0.0, description="Training duration seconds")
    status: str = Field(
        default="SUCCEEDED",
        description="Training run status (PENDING, RUNNING, SUCCEEDED, FAILED, CANCELLED)",
    )
    warnings: list[str] = Field(default_factory=list, description="Training warnings")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Training completion timestamp UTC"
    )


class CandidateTrialResult(BaseModel):
    """Trial outcome for an individual hyperparameter candidate (Phase 235)."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(..., description="Candidate trial identifier (e.g. trial_001)")
    trial_number: int = Field(..., ge=1, description="Trial sequence number")
    hyperparameters: dict[str, Any] = Field(..., description="Evaluated hyperparameter set")
    training_rows: int = Field(..., ge=0, description="Training dataset row count")
    validation_rows: int = Field(..., ge=0, description="Validation dataset row count")
    validation_metric: float = Field(..., description="Validation metric evaluation score")
    metric_name: str = Field(default="PR-AUC", description="Metric used for optimization")
    training_duration_seconds: float = Field(..., ge=0.0, description="Trial duration seconds")
    status: str = Field(
        default="SUCCEEDED", description="Trial status (SUCCEEDED, FAILED, REJECTED)"
    )  # noqa: E501
    random_seed: int = Field(default=42, description="Random seed used")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Trial timestamp UTC"
    )


class OptimizationManifest(BaseModel):
    """Manifest describing a hyperparameter optimization run (Phase 235)."""

    model_config = ConfigDict(extra="forbid")

    optimization_run_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Optimization run UUID"
    )
    training_dataset_id: uuid.UUID | None = Field(
        default=None, description="Source training dataset UUID"
    )
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    split_id: uuid.UUID | None = Field(default=None, description="Source split UUID")
    search_strategy: str = Field(..., description="Search strategy (GRID, RANDOM)")
    objective_metric: str = Field(default="PR-AUC", description="Target metric for optimization")
    search_space_summary: dict[str, Any] = Field(
        default_factory=dict, description="Configured hyperparameter search space bounds"
    )
    max_trials: int = Field(..., ge=1, description="Configured trial limit")
    random_seed: int = Field(default=42, description="Random seed used")
    candidate_count: int = Field(..., ge=0, description="Total completed trials count")
    best_candidate_id: str = Field(..., description="Selected best candidate trial ID")
    best_hyperparameters: dict[str, Any] = Field(
        ..., description="Selected best hyperparameter set"
    )  # noqa: E501
    best_validation_metric: float = Field(..., description="Selected best validation score")
    configuration_hash: str = Field(..., description="Optimization SHA-256 configuration hash")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Manifest creation timestamp UTC"
    )
