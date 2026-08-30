"""Unit tests for Class Imbalance Handling (Phase 231)."""

from __future__ import annotations

from app.ml.imbalance.imbalance_handler import ImbalanceHandler


def test_01_distribution_analysis_and_class_weights() -> None:
    """1. Test ImbalanceHandler class distribution analysis and weight computation."""
    handler = ImbalanceHandler(random_seed=42)
    records = [
        {"is_fraud": 0},
        {"is_fraud": 0},
        {"is_fraud": 0},
        {"is_fraud": 1},
    ]

    analysis = handler.analyze_distribution(records, target_column="is_fraud")
    assert analysis.total_samples == 4
    assert analysis.positive_samples == 1
    assert analysis.negative_samples == 3
    assert analysis.positive_ratio == 0.25
    assert analysis.imbalance_ratio == 3.0
    assert analysis.class_weights["0"] == 0.6667
    assert analysis.class_weights["1"] == 2.0


def test_02_resample_training_data_safety() -> None:
    """2. Test safe resampling strategies affecting training data exclusively."""
    handler = ImbalanceHandler(random_seed=42)
    training_records = [
        {"transaction_id": f"tx_{i}", "is_fraud": 0, "amount": 10.0 * i} for i in range(10)
    ] + [
        {"transaction_id": "tx_pos1", "is_fraud": 1, "amount": 500.0},
        {"transaction_id": "tx_pos2", "is_fraud": 1, "amount": 600.0},
    ]

    # Test Random Undersampling
    resample_under, meta_under = handler.resample_training_data(
        training_records, strategy="RANDOM_UNDERSAMPLING"
    )
    assert meta_under.selected_strategy == "RANDOM_UNDERSAMPLING"
    assert meta_under.training_only is True
    assert len(resample_under) == 4  # 2 pos + 2 neg

    # Test Random Oversampling
    resample_over, meta_over = handler.resample_training_data(
        training_records, strategy="RANDOM_OVERSAMPLING"
    )
    assert meta_over.selected_strategy == "RANDOM_OVERSAMPLING"
    assert len(resample_over) == 20  # 10 neg + 10 oversampled pos

    # Test SMOTE
    resample_smote, meta_smote = handler.resample_training_data(training_records, strategy="SMOTE")
    assert meta_smote.selected_strategy == "SMOTE"
    assert len(resample_smote) == 20
    assert any(r.get("is_synthetic") is True for r in resample_smote)
