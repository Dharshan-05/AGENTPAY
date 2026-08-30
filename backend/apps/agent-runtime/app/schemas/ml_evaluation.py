"""Pydantic Transport & Domain Schemas for Model Evaluation Foundation (Phases 236-242)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationThresholdConfig(BaseModel):
    """Configuration for classification decision threshold (Phase 236.7)."""

    model_config = ConfigDict(extra="forbid")

    threshold: float = Field(
        default=0.50, gt=0.0, lt=1.0, description="Probability cutoff threshold"
    )
    threshold_source: str = Field(
        default="CONFIGURATION",
        description="Origin source of threshold (CONFIGURATION, VALIDATION)",
    )


class PrecisionResult(BaseModel):
    """Structured metric result for Precision evaluation (Phase 237)."""

    model_config = ConfigDict(extra="forbid")

    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score TP / (TP + FP)")
    true_positives: int = Field(..., ge=0, description="True Positive count")
    false_positives: int = Field(..., ge=0, description="False Positive count")
    support: int = Field(..., ge=0, description="Total predicted positive samples (TP + FP)")
    threshold: float = Field(..., description="Applied decision threshold")
    warning: str | None = Field(default=None, description="Zero-division or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")


class RecallResult(BaseModel):
    """Structured metric result for Recall evaluation (Phase 238)."""

    model_config = ConfigDict(extra="forbid")

    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score TP / (TP + FN)")
    true_positives: int = Field(..., ge=0, description="True Positive count")
    false_negatives: int = Field(..., ge=0, description="False Negative count")
    support: int = Field(..., ge=0, description="Total ground truth positive samples (TP + FN)")
    threshold: float = Field(..., description="Applied decision threshold")
    warning: str | None = Field(default=None, description="Zero-division or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")


class F1Result(BaseModel):
    """Structured metric result for F1 score evaluation (Phase 239)."""

    model_config = ConfigDict(extra="forbid")

    f1: float = Field(..., ge=0.0, le=1.0, description="F1 score 2*P*R / (P + R)")
    true_positives: int = Field(..., ge=0, description="True Positive count")
    false_positives: int = Field(..., ge=0, description="False Positive count")
    false_negatives: int = Field(..., ge=0, description="False Negative count")
    support: int = Field(..., ge=0, description="Total positive support (2TP + FP + FN)")
    threshold: float = Field(..., description="Applied frozen decision threshold")
    threshold_source: str = Field(default="CONFIGURATION", description="Threshold origin source")
    warning: str | None = Field(default=None, description="Zero-division or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")
    metric_version: str = Field(default="1.0.0", description="Metric calculation logic version")


class RocAucResult(BaseModel):
    """Structured metric result for Receiver Operating Characteristic AUC evaluation (Phase 240)."""

    model_config = ConfigDict(extra="forbid")

    roc_auc: float | None = Field(
        default=None, ge=0.0, le=1.0, description="ROC-AUC score [0.0, 1.0] if defined"
    )
    positive_count: int = Field(..., ge=0, description="Actual ground truth positive count")
    negative_count: int = Field(..., ge=0, description="Actual ground truth negative count")
    sample_count: int = Field(..., ge=0, description="Total evaluated sample count")
    warning: str | None = Field(default=None, description="Single-class or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")
    metric_version: str = Field(default="1.0.0", description="Metric calculation logic version")


class PrAucResult(BaseModel):
    """Structured metric result for Precision-Recall AUC / Average Precision evaluation (Phase 241)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid")

    pr_auc: float | None = Field(
        default=None, ge=0.0, le=1.0, description="PR-AUC / Average Precision score if defined"
    )
    positive_count: int = Field(..., ge=0, description="Actual ground truth positive count")
    negative_count: int = Field(..., ge=0, description="Actual ground truth negative count")
    sample_count: int = Field(..., ge=0, description="Total evaluated sample count")
    warning: str | None = Field(default=None, description="Single-class or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")
    metric_definition: str = Field(
        default="AVERAGE_PRECISION", description="Explicit PR-AUC metric definition"
    )
    metric_version: str = Field(default="1.0.0", description="Metric calculation logic version")


class ConfusionMatrixResult(BaseModel):
    """Structured metric result for Confusion Matrix evaluation (Phase 242)."""

    model_config = ConfigDict(extra="forbid")

    true_positives: int = Field(..., ge=0, description="True Positive count (actual 1, pred 1)")
    true_negatives: int = Field(..., ge=0, description="True Negative count (actual 0, pred 0)")
    false_positives: int = Field(..., ge=0, description="False Positive count (actual 0, pred 1)")
    false_negatives: int = Field(..., ge=0, description="False Negative count (actual 1, pred 0)")
    total_samples: int = Field(..., ge=0, description="Total evaluated sample count")
    positive_support: int = Field(
        ..., ge=0, description="Actual positive ground truth count (TP+FN)"
    )  # noqa: E501
    negative_support: int = Field(
        ..., ge=0, description="Actual negative ground truth count (TN+FP)"
    )  # noqa: E501
    predicted_positives: int = Field(
        ..., ge=0, description="Total predicted positive count (TP+FP)"
    )  # noqa: E501
    predicted_negatives: int = Field(
        ..., ge=0, description="Total predicted negative count (TN+FN)"
    )  # noqa: E501
    true_positive_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="TPR / Sensitivity / Recall (TP / pos_support)"
    )
    true_negative_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="TNR / Specificity (TN / neg_support)"
    )
    false_positive_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="FPR / Fall-out (FP / neg_support)"
    )
    false_negative_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="FNR / Miss rate (FN / pos_support)"
    )
    threshold: float = Field(..., description="Applied decision threshold")
    threshold_source: str = Field(default="CONFIGURATION", description="Threshold origin source")
    warning: str | None = Field(default=None, description="Zero-denominator or quality warning")
    explanation: str = Field(..., description="Machine and human readable explanation")
    metric_version: str = Field(default="1.0.0", description="Metric calculation logic version")


class EvaluationResult(BaseModel):
    """Structured result of model evaluation execution (Phases 236-242)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    evaluation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Evaluation run UUID")
    model_candidate_id: str = Field(default="candidate_best", description="Target candidate ID")
    model_type: str = Field(default="XGBoost", description="Model family type")
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    split_partition: str = Field(
        default="TEST", description="Dataset partition evaluated (TEST, VALIDATION)"
    )
    feature_count: int = Field(..., ge=0, description="Validated feature count")
    feature_names: list[str] = Field(..., description="Validated bound feature names")
    sample_count: int = Field(..., ge=0, description="Evaluated sample count")
    positive_samples: int = Field(..., ge=0, description="Actual ground truth positive count")
    negative_samples: int = Field(..., ge=0, description="Actual ground truth negative count")
    predicted_positives: int = Field(..., ge=0, description="Predicted positive count")
    predicted_negatives: int = Field(..., ge=0, description="Predicted negative count")
    threshold_config: EvaluationThresholdConfig = Field(..., description="Applied threshold config")
    precision_result: PrecisionResult = Field(..., description="Precision metric outcome")
    recall_result: RecallResult = Field(..., description="Recall metric outcome")
    f1_result: F1Result | None = Field(default=None, description="F1 metric outcome (Phase 239)")
    roc_auc_result: RocAucResult | None = Field(
        default=None, description="ROC-AUC metric outcome (Phase 240)"
    )
    pr_auc_result: PrAucResult | None = Field(
        default=None, description="PR-AUC metric outcome (Phase 241)"
    )
    confusion_matrix_result: ConfusionMatrixResult | None = Field(
        default=None, description="Confusion Matrix outcome (Phase 242)"
    )
    status: str = Field(
        default="SUCCEEDED", description="Evaluation status (PENDING, RUNNING, SUCCEEDED, FAILED)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp UTC"
    )


class EvaluationManifest(BaseModel):
    """Immutable manifest recording reproducible model evaluation run (Phases 236-242)."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    evaluation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Evaluation run UUID")
    model_candidate_id: str = Field(..., description="Evaluated model candidate ID")
    dataset_fingerprint: str = Field(..., description="Dataset fingerprint tag")
    split_id: uuid.UUID | None = Field(default=None, description="Source split UUID")
    feature_versions: dict[str, str] = Field(..., description="Locked feature versions map")
    feature_names: list[str] = Field(..., description="Ordered bound feature names")
    threshold: float = Field(..., description="Applied decision threshold")
    threshold_source: str = Field(..., description="Threshold source (CONFIGURATION, VALIDATION)")
    sample_count: int = Field(..., ge=0, description="Evaluated sample count")
    positive_count: int = Field(..., ge=0, description="Actual positive count")
    negative_count: int = Field(..., ge=0, description="Actual negative count")
    precision: float = Field(..., ge=0.0, le=1.0, description="Evaluated precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Evaluated recall score")
    f1: float | None = Field(default=None, ge=0.0, le=1.0, description="Evaluated F1 score")
    roc_auc: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Evaluated ROC-AUC score"
    )
    pr_auc: float | None = Field(default=None, ge=0.0, le=1.0, description="Evaluated PR-AUC score")
    tp: int | None = Field(default=None, ge=0, description="True positive count")
    tn: int | None = Field(default=None, ge=0, description="True negative count")
    fp: int | None = Field(default=None, ge=0, description="False positive count")
    fn: int | None = Field(default=None, ge=0, description="False negative count")
    configuration_hash: str = Field(..., description="SHA-256 evaluation configuration hash")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Manifest creation timestamp UTC"
    )
