"""Hyperparameter Optimization Framework (Phase 235)."""

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
import uuid
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.optimization.search_space import HyperparameterSearchSpace
from app.ml.splitting.dataset_splitter import DatasetSplits
from app.ml.training.training_config import XGBoostTrainingConfig
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_training import CandidateTrialResult, ModelTrainingResult, OptimizationManifest

logger = logging.getLogger("fraudguard.ml.optimization")


class HyperparameterOptimizer:
    """Production Hyperparameter Optimization Engine operating on Validation Set (Phase 235)."""

    def __init__(
        self,
        config: MLPipelineConfig | None = None,
        trainer: XGBoostTrainer | None = None,
    ) -> None:
        self.config = config or get_default_ml_config()
        self.trainer = trainer or XGBoostTrainer(config=self.config)

    def _compute_validation_metric(
        self, y_true: Any, y_prob: Any, metric_name: str = "PR-AUC"
    ) -> float:
        """Compute minority-class validation metric without evaluating test set (Phase 235.1)."""  # noqa: E501
        if len(np.unique(y_true)) < 2:
            return 0.0

        if metric_name == "PR-AUC":
            val = float(average_precision_score(y_true, y_prob))
        elif metric_name == "ROC-AUC":
            val = float(roc_auc_score(y_true, y_prob))
        elif metric_name == "F1":
            y_pred = (y_prob >= 0.5).astype(int)
            val = float(f1_score(y_true, y_pred, zero_division=0))
        else:
            val = float(average_precision_score(y_true, y_prob))

        return round(val, 6)

    def optimize(
        self,
        splits: DatasetSplits,
        search_space: HyperparameterSearchSpace | None = None,
        strategy: str = "RANDOM",
        max_trials: int = 5,
        objective_metric: str = "PR-AUC",
        random_seed: int | None = None,
    ) -> tuple[Any, ModelTrainingResult, OptimizationManifest, list[CandidateTrialResult]]:
        """Execute deterministic hyperparameter optimization strictly on validation set (Phase 235)."""  # noqa: E501
        seed = random_seed if random_seed is not None else self.config.random_seed
        rng = random.Random(seed)
        space = search_space or HyperparameterSearchSpace()

        # 1. MANDATORY TEST SET ISOLATION ASSERTION
        if splits.test_dataset.X is None:
            raise ValueError("Invalid splits object.")

        val_ds = splits.validation_dataset
        if not val_ds.X or not val_ds.y:
            raise ValueError("Validation set must be non-empty for hyperparameter optimization.")

        # Prepare validation ground truth & feature matrix once
        val_X_mat = self.trainer._convert_to_matrix(val_ds.X, val_ds.feature_names)
        val_y_arr = np.array(val_ds.y, dtype=np.int32)

        candidate_trials: list[CandidateTrialResult] = []
        best_model: Any = None
        best_training_result: ModelTrainingResult | None = None
        best_trial: CandidateTrialResult | None = None

        logger.info(
            "Starting hyperparameter optimization (%s strategy, max_trials=%d, metric=%s, seed=%d)",
            strategy,
            max_trials,
            objective_metric,
            seed,
        )

        for trial_num in range(1, max_trials + 1):
            t_start = time.time()
            trial_id = f"trial_{trial_num:03d}"

            # Generate hyperparameter candidate parameters
            if strategy == "GRID":
                # Deterministic grid sample based on trial_num index
                md = space.max_depth_options[(trial_num - 1) % len(space.max_depth_options)]
                lr = space.learning_rate_options[(trial_num - 1) % len(space.learning_rate_options)]
                ne = space.n_estimators_options[(trial_num - 1) % len(space.n_estimators_options)]
                sub = space.subsample_options[0]
                col = space.colsample_bytree_options[0]
                spw = space.scale_pos_weight_options[0]
            else:  # RANDOM strategy
                md = rng.choice(space.max_depth_options)
                lr = rng.choice(space.learning_rate_options)
                ne = rng.choice(space.n_estimators_options)
                sub = rng.choice(space.subsample_options)
                col = rng.choice(space.colsample_bytree_options)
                spw = rng.choice(space.scale_pos_weight_options)

            train_cfg = XGBoostTrainingConfig(
                max_depth=md,
                learning_rate=lr,
                n_estimators=ne,
                subsample=sub,
                colsample_bytree=col,
                scale_pos_weight=spw,
                random_state=seed,
            )

            # Fit candidate model on Train set, evaluate on Validation set
            try:
                model, t_res = self.trainer.train(splits, training_config=train_cfg)

                # Predict probabilities on VALIDATION set ONLY
                val_probs = model.predict_proba(val_X_mat)[:, 1]
                val_metric = self._compute_validation_metric(
                    val_y_arr, val_probs, metric_name=objective_metric
                )
                trial_status = "SUCCEEDED"
            except Exception as exc:
                logger.error("Trial %s failed: %s", trial_id, exc)
                val_metric = 0.0
                trial_status = "FAILED"

            duration = round(time.time() - t_start, 4)

            trial_rec = CandidateTrialResult(
                candidate_id=trial_id,
                trial_number=trial_num,
                hyperparameters=train_cfg.to_xgb_params(),
                training_rows=len(splits.train_dataset.X),
                validation_rows=len(splits.validation_dataset.X),
                validation_metric=val_metric,
                metric_name=objective_metric,
                training_duration_seconds=duration,
                status=trial_status,
                random_seed=seed,
            )
            candidate_trials.append(trial_rec)

            # Deterministic Best Candidate Selection & Tie-Breaking
            # Rule: Higher validation metric wins -> if equal, lower trial_number (first seen)
            if trial_status == "SUCCEEDED":
                if best_trial is None or val_metric > best_trial.validation_metric:
                    best_trial = trial_rec
                    best_model = model
                    best_training_result = t_res

        if best_trial is None or best_model is None or best_training_result is None:
            raise RuntimeError(
                "Hyperparameter optimization failed: no valid candidate trial succeeded."
            )  # noqa: E501

        opt_run_id = uuid.uuid4()
        config_payload = {
            "strategy": strategy,
            "max_trials": max_trials,
            "objective_metric": objective_metric,
            "seed": seed,
            "search_space": space.to_summary_dict(),
        }
        cfg_hash = hashlib.sha256(json.dumps(config_payload, sort_keys=True).encode()).hexdigest()

        opt_manifest = OptimizationManifest(
            optimization_run_id=opt_run_id,
            training_dataset_id=splits.train_dataset.manifest.training_dataset_id,
            dataset_fingerprint=splits.train_dataset.manifest.dataset_fingerprint,
            split_id=splits.split_manifest.split_id,
            search_strategy=strategy,
            objective_metric=objective_metric,
            search_space_summary=space.to_summary_dict(),
            max_trials=max_trials,
            random_seed=seed,
            candidate_count=len(candidate_trials),
            best_candidate_id=best_trial.candidate_id,
            best_hyperparameters=best_trial.hyperparameters,
            best_validation_metric=best_trial.validation_metric,
            configuration_hash=cfg_hash,
        )

        logger.info(
            "Optimization complete (Run ID: %s, Best Trial: %s, Best %s: %.4f)",
            opt_run_id,
            best_trial.candidate_id,
            objective_metric,
            best_trial.validation_metric,
        )

        return best_model, best_training_result, opt_manifest, candidate_trials
