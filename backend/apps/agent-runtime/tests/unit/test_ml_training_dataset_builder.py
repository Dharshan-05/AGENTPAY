"""Unit tests for Training Dataset Preparation (Phase 232)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder


def test_01_build_training_dataset_feature_target_separation() -> None:
    """1. Test feature/target separation and version locking manifest generation."""
    builder = TrainingDatasetBuilder()
    tenant_id = uuid.uuid4()
    records = [
        {
            "transaction_id": "tx1",
            "tenant_id": str(tenant_id),
            "amount": Decimal("100.00"),
            "tx_amount_log": 4.61,
            "is_fraud": 0,
        },
        {
            "transaction_id": "tx2",
            "tenant_id": str(tenant_id),
            "amount": Decimal("250.00"),
            "tx_amount_log": 5.52,
            "is_fraud": 1,
        },
    ]

    dataset = builder.build_training_dataset(records, target_column="is_fraud", tenant_id=tenant_id)
    assert len(dataset.X) == 2
    assert dataset.y == [0, 1]
    assert dataset.target_name == "is_fraud"
    assert "is_fraud" not in dataset.X[0]
    assert dataset.manifest.row_count == 2
    assert dataset.manifest.leakage_status is False
    assert dataset.manifest.tenant_id == str(tenant_id)


def test_02_target_leakage_and_cross_tenant_rejection() -> None:
    """2. Test target leakage rejection and cross-tenant boundary validation."""
    builder = TrainingDatasetBuilder()
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()

    # Cross-tenant record rejection
    cross_records = [
        {"transaction_id": "tx1", "tenant_id": str(t1), "amount": 100.0, "is_fraud": 0},
        {"transaction_id": "tx2", "tenant_id": str(t2), "amount": 200.0, "is_fraud": 1},
    ]
    with pytest.raises(ValueError, match="Cross-tenant record detected"):
        builder.build_training_dataset(cross_records, tenant_id=t1)

    # Target leakage keyword detection
    leakage_records = [
        {
            "transaction_id": "tx1",
            "tenant_id": str(t1),
            "amount": 100.0,
            "post_outcome_status": "refunded",
            "is_fraud": 0,
        },  # noqa: E501
    ]
    dataset = builder.build_training_dataset(leakage_records, tenant_id=t1)
    assert "post_outcome_status" not in dataset.X[0]
    assert dataset.manifest.leakage_status is True
