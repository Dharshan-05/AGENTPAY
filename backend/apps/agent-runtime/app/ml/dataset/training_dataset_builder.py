"""Canonical Training Dataset Preparation Layer (Phase 232)."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.ml.config.ml_config import (  # noqa: E501
    MLPipelineConfig,
    compute_dataset_fingerprint,
    get_default_ml_config,
)
from app.ml.feature_store.feature_store import FeatureStore
from app.ml.feature_validation.feature_validator import FeatureValidator
from app.ml.validation.dataset_validator import DatasetValidator
from app.schemas.ml_training import TrainingDatasetManifest

logger = logging.getLogger("fraudguard.ml.dataset")


@dataclass
class TrainingDataset:
    """Canonical container holding features X, target y, and metadata manifest (Phase 232)."""

    X: list[dict[str, Any]]
    y: list[int]
    feature_names: list[str]
    target_name: str
    manifest: TrainingDatasetManifest


class TrainingDatasetBuilder:
    """Production Training Dataset Preparation Engine (Phase 232)."""

    def __init__(
        self,
        config: MLPipelineConfig | None = None,
        feature_store: FeatureStore | None = None,
        dataset_validator: DatasetValidator | None = None,
        feature_validator: FeatureValidator | None = None,
    ) -> None:
        self.config = config or get_default_ml_config()
        self.feature_store = feature_store or FeatureStore(config=self.config)
        self.dataset_validator = dataset_validator or DatasetValidator(config=self.config)
        self.feature_validator = feature_validator or FeatureValidator(config=self.config)

    def build_training_dataset(
        self,
        records: list[dict[str, Any]],
        target_column: str = "is_fraud",
        allowed_statuses: tuple[str, ...] = ("ACTIVE",),
        tenant_id: uuid.UUID | None = None,
        execution_id: uuid.UUID | None = None,
    ) -> TrainingDataset:
        """Build canonical FraudGuard training dataset with feature/target separation & version locking (Phase 232)."""  # noqa: E501
        logger.info("Building canonical training dataset from %d records", len(records))

        if not records:
            raise ValueError("Cannot build training dataset from empty record list.")

        tenant_str = str(tenant_id) if tenant_id else None

        # 1. Feature Eligibility & Version Locking from FeatureStore
        active_records = self.feature_store.list_active_features()
        feature_versions: dict[str, str] = {}

        if active_records:
            for fs_rec in active_records:
                if fs_rec.status in allowed_statuses:
                    feature_versions[fs_rec.name] = fs_rec.version
        else:
            # Fallback for dynamic feature records if registry not yet populated
            sample = records[0]
            for k in sample.keys():
                if k not in (
                    target_column,
                    "tenant_id",
                    "agent_id",
                    "transaction_id",
                    "created_at",
                ):  # noqa: E501
                    feature_versions[k] = "1.0.0"

        # Leakage defense keywords to explicitly exclude from X
        prohibited_keywords = {
            target_column.lower(),
            "is_fraud",
            "fraud_label",
            "post_outcome",
            "investigation_result",
            "future_signal",
        }

        X: list[dict[str, Any]] = []
        y: list[int] = []

        now_utc = datetime.now(UTC)
        leakage_detected = False

        for idx, rec in enumerate(records):
            # Tenant Boundary Check
            if tenant_str and rec.get("tenant_id") and str(rec["tenant_id"]) != tenant_str:
                raise ValueError(
                    f"Cross-tenant record detected at row {idx} (expected {tenant_str}, got {rec.get('tenant_id')})"  # noqa: E501
                )

            # Target Extract & Validate
            raw_target = rec.get(target_column)
            if raw_target is None:
                raise ValueError(f"Missing target label '{target_column}' at record index {idx}")

            try:
                target_val = int(raw_target)
                if target_val not in (0, 1):
                    raise ValueError(f"Invalid target label value '{raw_target}' at index {idx}")
                y.append(target_val)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Unparseable target label '{raw_target}' at index {idx}") from exc

            # Feature Extract & Target Leakage Defense
            feat_dict: dict[str, Any] = {}
            for k, v in rec.items():
                k_lower = k.lower()
                if k == target_column or any(kw in k_lower for kw in prohibited_keywords):
                    if k != target_column:
                        leakage_detected = True
                        logger.warning("Target leakage keyword detected in feature '%s'", k)
                    continue

                # Point-in-time check if created_at present
                if k == "created_at":
                    try:
                        if isinstance(v, str):
                            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                        elif isinstance(v, datetime):
                            dt = v
                        else:
                            dt = None
                        if dt and dt.replace(tzinfo=UTC) > now_utc:
                            leakage_detected = True
                    except Exception:
                        pass

                feat_dict[k] = v

            X.append(feat_dict)

        metadata_keys = {"transaction_id", "tenant_id", "agent_id", "created_at"}
        feature_names = sorted([k for k in X[0].keys() if k not in metadata_keys]) if X else []
        dataset_fingerprint = compute_dataset_fingerprint(X)

        manifest = TrainingDatasetManifest(
            dataset_version=self.config.dataset_version,
            dataset_fingerprint=dataset_fingerprint,
            feature_versions=feature_versions,
            preprocessor_version=self.config.preprocessing_version,
            schema_version=self.config.schema_version,
            pipeline_version=self.config.pipeline_version,
            target_definition=target_column,
            row_count=len(X),
            feature_count=len(feature_names),
            quality_score=Decimal("1.00") if not leakage_detected else Decimal("0.50"),
            leakage_status=leakage_detected,
            tenant_id=tenant_str,
            execution_id=execution_id,
            created_at=datetime.now(UTC),
        )

        return TrainingDataset(
            X=X,
            y=y,
            feature_names=feature_names,
            target_name=target_column,
            manifest=manifest,
        )
