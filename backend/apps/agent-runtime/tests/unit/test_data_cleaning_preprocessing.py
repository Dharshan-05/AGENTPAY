"""Unit tests for Data Cleaning and Data Preprocessing (Phases 219-220)."""

from __future__ import annotations

from app.ml.cleaning.data_cleaner import DataCleaner
from app.ml.preprocessing.data_preprocessor import DataPreprocessor


def test_01_data_cleaner_audits_and_quarantine() -> None:
    """1. Test DataCleaner rule auditing and quarantine record generation."""
    cleaner = DataCleaner()
    raw_records = [
        {"transaction_id": "tx1", "amount": "100.00", "currency": "usd"},
        {"transaction_id": "tx1", "amount": "100.00", "currency": "usd"},  # duplicate
        {"transaction_id": "tx2", "amount": "-50.00", "currency": "USD"},  # invalid negative
    ]

    cleaned, stats = cleaner.clean_dataset(raw_records)
    assert len(cleaned) == 1
    assert stats.input_rows == 3
    assert stats.clean_rows == 1
    assert stats.duplicate_rows == 1
    assert stats.invalid_rows == 1
    assert stats.quarantined_rows == 2
    assert len(stats.rule_audits) == 2
    assert len(cleaner.quarantine_vault) == 2


def test_02_preprocessor_artifact_metadata_and_stability() -> None:
    """2. Test DataPreprocessor artifact versioning and NaN numerical stability."""
    train_data = [
        {"amount": 10.0, "category": "electronics"},
        {"amount": 30.0, "category": "retail"},
    ]
    test_data = [
        {"amount": float("nan"), "category": "electronics"},  # NaN value handled safely
        {"amount": 50.0, "category": "unknown_cat"},
    ]

    processor = DataPreprocessor()
    processor.fit(
        train_data,
        numerical_columns=["amount"],
        categorical_columns=["category"],
        fit_dataset_version="v2",
    )  # noqa: E501

    assert processor.state.is_fitted is True
    assert processor.state.fit_dataset_version == "v2"
    assert processor.state.preprocessor_version == "2.0"

    transformed = processor.transform(test_data)
    assert len(transformed) == 2
    assert transformed[0]["amount_scaled"] == 0.0  # Imputed with mean
    assert transformed[1]["category_encoded"] == 0
