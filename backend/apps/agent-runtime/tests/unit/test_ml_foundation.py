"""Unit tests for ML Foundation, Dataset Integration, and Dataset Validation (Phases 216-218)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from app.ml.config.ml_config import (  # noqa: E501
    PipelineExecutionTracker,
    compute_dataset_fingerprint,
    get_default_ml_config,
)
from app.ml.integration.dataset_loader import DatasetLoader
from app.ml.validation.dataset_validator import DatasetValidator


def test_01_ml_config_manifest_and_execution_tracker() -> None:
    """1. Test ML configuration reproducibility manifest generation and execution tracking."""
    config = get_default_ml_config("test")
    manifest = config.generate_reproducibility_manifest(code_version="v2.0")
    assert manifest.pipeline_version == "1.0.0"
    assert manifest.configuration_hash == config.compute_configuration_hash()
    assert manifest.code_version == "v2.0"

    tracker = PipelineExecutionTracker()
    exec_rec = tracker.start_execution("run_101")
    assert exec_rec.status == "RUNNING"
    completed = tracker.complete_execution(exec_rec.execution_id, status="SUCCEEDED")
    assert completed.status == "SUCCEEDED"
    assert completed.completed_at is not None


def test_02_dataset_loader_fingerprinting_and_snapshots() -> None:
    """2. Test DatasetLoader immutable snapshots and content fingerprinting."""
    loader = DatasetLoader()
    t1 = uuid.uuid4()

    records = [
        {"transaction_id": "tx1", "tenant_id": str(t1), "amount": "100.00", "currency": "USD"},
    ]

    clean_records, meta = loader.load_raw_batch_records(t1, records)
    assert len(clean_records) == 1
    assert meta.fingerprint == compute_dataset_fingerprint(clean_records)

    snapshot = loader.create_snapshot("test_ds", clean_records, version_tag="v1")
    assert snapshot.fingerprint == meta.fingerprint
    assert snapshot.dataset_version == "v1"


def test_03_dataset_validator_quality_scoring_and_future_timestamp() -> None:
    """3. Test DatasetValidator quality score computation and temporal future timestamp detection."""  # noqa: E501
    validator = DatasetValidator()
    tenant_id = uuid.uuid4()

    records = [
        {
            "transaction_id": "tx1",
            "tenant_id": str(tenant_id),
            "amount": Decimal("50.00"),
            "currency": "USD",
        },  # noqa: E501
        {
            "transaction_id": "tx2",
            "tenant_id": str(tenant_id),
            "amount": Decimal("100.00"),
            "currency": "USD",
            "created_at": "2099-01-01T00:00:00Z",
        },  # future timestamp  # noqa: E501
    ]

    res = validator.validate_dataset("test_ds", records, tenant_id=tenant_id)
    assert res.valid is False
    assert res.quality_score < Decimal("1.00")
    assert any(v.code == "FUTURE_TIMESTAMPS_DETECTED" for v in res.violations)
