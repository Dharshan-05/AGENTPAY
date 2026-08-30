"""Unit tests for Train / Validation / Test Splitting (Phase 233)."""

from __future__ import annotations

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.splitting.dataset_splitter import DatasetSplitter


def test_01_temporal_split_partitioning_and_boundaries() -> None:
    """1. Test temporal split partitioning, chronological order, and temporal boundaries."""
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(10):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 10.0 * (i + 1),
                "created_at": f"2026-08-26T10:0{i}:00Z",
                "is_fraud": 1 if i % 4 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()

    splits = splitter.split_dataset(
        dataset, strategy="TEMPORAL", train_ratio=0.70, validation_ratio=0.15, test_ratio=0.15
    )  # noqa: E501
    assert len(splits.train_dataset.X) == 7
    assert len(splits.validation_dataset.X) == 1
    assert len(splits.test_dataset.X) == 2

    assert splits.split_manifest.strategy == "TEMPORAL"
    assert "train_max" in splits.split_manifest.temporal_boundaries
    assert "val_min" in splits.split_manifest.temporal_boundaries
    assert "test_min" in splits.split_manifest.temporal_boundaries


def test_02_stratified_and_random_splits_disjointness() -> None:
    """2. Test stratified/random splits and partition disjointness validation."""
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(20):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 50.0 * (i + 1),
                "is_fraud": 1 if i < 5 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()

    splits = splitter.split_dataset(dataset, strategy="STRATIFIED", random_seed=42)
    assert splits.split_manifest.strategy == "STRATIFIED"
    assert splits.train_dataset.y.count(1) > 0
    assert splits.validation_dataset.y.count(1) >= 0

    train_ids = {r["transaction_id"] for r in splits.train_dataset.X}
    val_ids = {r["transaction_id"] for r in splits.validation_dataset.X}
    test_ids = {r["transaction_id"] for r in splits.test_dataset.X}

    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(test_ids)
    assert val_ids.isdisjoint(test_ids)
