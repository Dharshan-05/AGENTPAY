"""ML Data Pipeline Deterministic Configuration & Foundation (Phase 216)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.schemas.ml_foundation import PipelineExecutionRecord, PipelineReproducibilityManifest

logger = logging.getLogger("fraudguard.ml.config")


@dataclass(frozen=True)
class MLPipelineConfig:
    """Production-grade ML Pipeline Configuration (Phase 216)."""

    pipeline_version: str = "1.0.0"
    dataset_version: str = "1.0.0"
    feature_pipeline_version: str = "1.0.0"
    schema_version: str = "1.0"
    preprocessing_version: str = "1.0.0"
    random_seed: int = 42
    environment: str = "production"
    strict_validation: bool = True
    allow_cold_start_imputation: bool = True
    max_missing_ratio_threshold: float = 0.30
    feature_flags: dict[str, bool] = field(
        default_factory=lambda: {
            "enable_velocity_features": True,
            "enable_intent_features": True,
            "enable_behaviour_features": True,
            "enable_policy_features": True,
            "enable_trust_features": True,
            "enable_merchant_features": True,
        }
    )

    def compute_configuration_hash(self) -> str:
        """Compute SHA-256 hash of configuration parameters for reproducibility tracking."""
        payload = {
            "pipeline_version": self.pipeline_version,
            "dataset_version": self.dataset_version,
            "feature_pipeline_version": self.feature_pipeline_version,
            "schema_version": self.schema_version,
            "preprocessing_version": self.preprocessing_version,
            "random_seed": self.random_seed,
            "environment": self.environment,
            "strict_validation": self.strict_validation,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def generate_reproducibility_manifest(
        self, code_version: str = "git-sha-latest"
    ) -> PipelineReproducibilityManifest:
        """Generate a deterministic pipeline reproducibility manifest (Phase 216)."""
        return PipelineReproducibilityManifest(
            pipeline_version=self.pipeline_version,
            dataset_version=self.dataset_version,
            schema_version=self.schema_version,
            feature_version=self.feature_pipeline_version,
            preprocessing_version=self.preprocessing_version,
            code_version=code_version,
            configuration_hash=self.compute_configuration_hash(),
            dependency_snapshot={"pydantic": "2.x", "sqlalchemy": "2.x", "fastapi": "0.x"},
            random_seed=self.random_seed,
            execution_timestamp=datetime.now(UTC),
        )

    def to_metadata_dict(self) -> dict[str, Any]:
        """Return non-sensitive metadata summary for reproducibility tracking."""
        return {
            "pipeline_version": self.pipeline_version,
            "dataset_version": self.dataset_version,
            "feature_pipeline_version": self.feature_pipeline_version,
            "schema_version": self.schema_version,
            "preprocessing_version": self.preprocessing_version,
            "random_seed": self.random_seed,
            "environment": self.environment,
            "strict_validation": self.strict_validation,
            "configuration_hash": self.compute_configuration_hash(),
        }


def compute_dataset_fingerprint(records: list[dict[str, Any]]) -> str:
    """Compute deterministic dataset fingerprint based on content and structure (Phase 216)."""
    if not records:
        return hashlib.sha256(b"empty_dataset").hexdigest()

    fingerprint_items: list[str] = []
    for r in sorted(records, key=lambda x: str(x.get("transaction_id") or x.get("id") or "")):
        tx_id = str(r.get("transaction_id") or r.get("id") or "")
        amt = str(r.get("amount") or "")
        curr = str(r.get("currency") or "")
        fingerprint_items.append(f"{tx_id}:{amt}:{curr}")

    content_str = "|".join(fingerprint_items).encode("utf-8")
    return hashlib.sha256(content_str).hexdigest()


class PipelineExecutionTracker:
    """Tracker for managing execution identity, run IDs, and statuses (Phase 216)."""

    def __init__(self, pipeline_version: str = "1.0.0") -> None:
        self.pipeline_version = pipeline_version
        self.active_runs: dict[uuid.UUID, PipelineExecutionRecord] = {}

    def start_execution(self, run_id: str) -> PipelineExecutionRecord:
        """Start a new pipeline execution run."""
        rec = PipelineExecutionRecord(
            run_id=run_id,
            pipeline_version=self.pipeline_version,
            status="RUNNING",
            started_at=datetime.now(UTC),
        )
        self.active_runs[rec.execution_id] = rec
        logger.info("Started pipeline execution run %s (ID: %s)", run_id, rec.execution_id)
        return rec

    def complete_execution(
        self, execution_id: uuid.UUID, status: str = "SUCCEEDED"
    ) -> PipelineExecutionRecord:  # noqa: E501
        """Complete an active pipeline execution run."""
        rec = self.active_runs.get(execution_id)
        if not rec:
            raise KeyError(f"Execution ID {execution_id} not found")

        updated_rec = PipelineExecutionRecord(
            execution_id=rec.execution_id,
            run_id=rec.run_id,
            pipeline_version=rec.pipeline_version,
            status=status,
            started_at=rec.started_at,
            completed_at=datetime.now(UTC),
        )
        self.active_runs[execution_id] = updated_rec
        logger.info("Completed pipeline execution ID %s with status %s", execution_id, status)
        return updated_rec


def get_default_ml_config(environment: str = "production") -> MLPipelineConfig:
    """Factory helper returning environment-scoped MLPipelineConfig."""
    logger.info("Initializing MLPipelineConfig for environment: %s", environment)
    return MLPipelineConfig(environment=environment)
