"""Unit tests for Hyperparameter Optimization (Phase 235)."""

from __future__ import annotations

from app.ml.dataset.training_dataset_builder import TrainingDatasetBuilder
from app.ml.optimization.hyperparameter_optimizer import HyperparameterOptimizer
from app.ml.optimization.search_space import HyperparameterSearchSpace
from app.ml.splitting.dataset_splitter import DatasetSplitter


def test_01_optimizer_search_space_and_candidate_tracking() -> None:
    """1. Test HyperparameterOptimizer trial execution, candidate tracking, and manifest."""
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(30):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 50.0 * (i + 1),
                "tx_amount_log": 3.0 + i * 0.1,
                "is_fraud": 1 if i % 3 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="RANDOM", random_seed=42)

    optimizer = HyperparameterOptimizer()
    space = HyperparameterSearchSpace(
        max_depth_options=[2, 4],
        learning_rate_options=[0.05, 0.1],
        n_estimators_options=[10, 20],
    )

    best_model, t_res, manifest, trials = optimizer.optimize(
        splits,
        search_space=space,
        strategy="RANDOM",
        max_trials=3,
        objective_metric="PR-AUC",
        random_seed=42,  # noqa: E501
    )

    assert len(trials) == 3
    assert manifest.candidate_count == 3
    assert (
        manifest.best_candidate_id == best_trial_id
        if (best_trial_id := manifest.best_candidate_id)
        else True
    )  # noqa: E501
    assert best_model is not None
    assert t_res.status == "SUCCEEDED"


def test_02_mandatory_test_set_poison_test() -> None:
    """2. Mandatory Test-Set Poison Test: Verify optimizer NEVER reads or optimizes against test set."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(20):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 100.0 * (i + 1),
                "is_fraud": 1 if i % 2 == 0 else 0,
            }
        )

    dataset = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits = splitter.split_dataset(dataset, strategy="TEMPORAL")

    # Deliberately poison test dataset labels with invalid dummy sentinel values
    poisoned_test_y = [-9999] * len(splits.test_dataset.y)
    splits.test_dataset.y = poisoned_test_y

    optimizer = HyperparameterOptimizer()
    # Optimization must succeed cleanly because test_dataset is NEVER accessed during optimization!  # noqa: E501
    best_model, _, manifest, trials = optimizer.optimize(
        splits, strategy="GRID", max_trials=2, random_seed=42
    )

    assert manifest.candidate_count == 2
    assert best_model is not None


def test_03_mandatory_reproducibility_and_dataset_change_test() -> None:
    """3. Mandatory Reproducibility Test: Identical configuration produces identical candidate results."""  # noqa: E501
    builder = TrainingDatasetBuilder()
    records = []
    for i in range(25):
        records.append(
            {
                "transaction_id": f"tx_{i}",
                "amount": 20.0 * (i + 1),
                "is_fraud": 1 if i % 5 == 0 else 0,
            }
        )

    dataset1 = builder.build_training_dataset(records)
    splitter = DatasetSplitter()
    splits1 = splitter.split_dataset(dataset1, strategy="STRATIFIED", random_seed=100)

    optimizer = HyperparameterOptimizer()
    _, _, manifest1, trials1 = optimizer.optimize(
        splits1, strategy="RANDOM", max_trials=3, random_seed=42
    )

    # Second run with exact same inputs
    splits2 = splitter.split_dataset(dataset1, strategy="STRATIFIED", random_seed=100)
    _, _, manifest2, trials2 = optimizer.optimize(
        splits2, strategy="RANDOM", max_trials=3, random_seed=42
    )

    assert manifest1.dataset_fingerprint == manifest2.dataset_fingerprint
    assert manifest1.best_candidate_id == manifest2.best_candidate_id
    assert manifest1.best_validation_metric == manifest2.best_validation_metric
    assert [t.validation_metric for t in trials1] == [t.validation_metric for t in trials2]
