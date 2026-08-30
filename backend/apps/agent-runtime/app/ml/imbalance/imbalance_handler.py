"""Class Imbalance Handling Layer (Phase 231)."""

from __future__ import annotations

import logging
import random
from typing import Any

from app.schemas.ml_training import ImbalanceAnalysisResult

logger = logging.getLogger("fraudguard.ml.imbalance")


class ImbalanceHandler:
    """Production Class Imbalance Analysis & Safe Resampling Engine (Phase 231)."""

    def __init__(self, random_seed: int = 42) -> None:
        self.random_seed = random_seed

    def analyze_distribution(
        self, records: list[dict[str, Any]], target_column: str = "is_fraud"
    ) -> ImbalanceAnalysisResult:
        """Analyze class label distribution and quality constraints (Phase 231.1)."""
        warnings: list[str] = []
        if not records:
            warnings.append("Dataset is empty.")
            return ImbalanceAnalysisResult(
                total_samples=0,
                positive_samples=0,
                negative_samples=0,
                positive_ratio=0.0,
                negative_ratio=0.0,
                imbalance_ratio=0.0,
                class_counts={"0": 0, "1": 0},
                selected_strategy="NONE",
                random_seed=self.random_seed,
                warnings=warnings,
            )

        pos_count = 0
        neg_count = 0
        missing_target_count = 0
        invalid_label_count = 0

        for r in records:
            lbl = r.get(target_column)
            if lbl is None:
                missing_target_count += 1
                continue

            try:
                val = int(lbl)
                if val == 1:
                    pos_count += 1
                elif val == 0:
                    neg_count += 1
                else:
                    invalid_label_count += 1
            except (ValueError, TypeError):
                invalid_label_count += 1

        total = pos_count + neg_count
        if total == 0:
            warnings.append("No valid binary target labels found.")
            return ImbalanceAnalysisResult(
                total_samples=0,
                positive_samples=0,
                negative_samples=0,
                positive_ratio=0.0,
                negative_ratio=0.0,
                imbalance_ratio=0.0,
                class_counts={"0": 0, "1": 0},
                selected_strategy="NONE",
                random_seed=self.random_seed,
                warnings=warnings,
            )

        if missing_target_count > 0:
            warnings.append(f"Found {missing_target_count} records with missing target labels.")
        if invalid_label_count > 0:
            warnings.append(f"Found {invalid_label_count} records with non-binary target labels.")

        pos_ratio = round(pos_count / total, 4)
        neg_ratio = round(neg_count / total, 4)
        imbalance_ratio = round(neg_count / max(1, pos_count), 2)

        if pos_count == 0:
            warnings.append("Dataset contains 0 positive (fraud) instances.")
        elif neg_count == 0:
            warnings.append("Dataset contains 0 negative (legitimate) instances.")
        elif imbalance_ratio > 10.0:
            warnings.append(
                f"Severe class imbalance detected: ratio {imbalance_ratio}:1 (neg:pos)."
            )

        class_weights = self.compute_class_weights(pos_count, neg_count)

        return ImbalanceAnalysisResult(
            total_samples=total,
            positive_samples=pos_count,
            negative_samples=neg_count,
            positive_ratio=pos_ratio,
            negative_ratio=neg_ratio,
            imbalance_ratio=imbalance_ratio,
            class_counts={"0": neg_count, "1": pos_count},
            selected_strategy="NONE",
            class_weights=class_weights,
            training_only=True,
            random_seed=self.random_seed,
            warnings=warnings,
        )

    def compute_class_weights(self, pos_count: int, neg_count: int) -> dict[str, float]:
        """Compute balanced class weights for model loss functions (Phase 231.4)."""
        total = pos_count + neg_count
        if total == 0 or pos_count == 0 or neg_count == 0:
            return {"0": 1.0, "1": 1.0}

        w0 = round(total / (2.0 * neg_count), 4)
        w1 = round(
            min(50.0, total / (2.0 * pos_count)), 4
        )  # Cap extreme weight spikes for numerical stability  # noqa: E501
        return {"0": w0, "1": w1}

    def resample_training_data(
        self,
        training_records: list[dict[str, Any]],
        target_column: str = "is_fraud",
        strategy: str = "CLASS_WEIGHT",
        random_seed: int | None = None,
    ) -> tuple[list[dict[str, Any]], ImbalanceAnalysisResult]:
        """Apply safe resampling exclusively to training data (Phase 231.2 & 231.3)."""
        seed = random_seed if random_seed is not None else self.random_seed
        rng = random.Random(seed)

        analysis = self.analyze_distribution(training_records, target_column=target_column)
        if analysis.total_samples == 0 or strategy == "NONE" or strategy == "CLASS_WEIGHT":
            result = analysis.model_copy(update={"selected_strategy": strategy})
            return training_records, result

        pos_records = [r for r in training_records if str(r.get(target_column)) == "1"]
        neg_records = [r for r in training_records if str(r.get(target_column)) == "0"]

        if not pos_records or not neg_records:
            analysis.warnings.append(
                f"Resampling strategy {strategy} skipped: minority or majority class is missing."
            )
            return training_records, analysis.model_copy(update={"selected_strategy": "NONE"})

        resampled_records: list[dict[str, Any]] = []

        if strategy == "RANDOM_UNDERSAMPLING":
            sampled_neg = rng.sample(neg_records, k=min(len(neg_records), len(pos_records)))
            resampled_records = pos_records + sampled_neg
            rng.shuffle(resampled_records)

        elif strategy == "RANDOM_OVERSAMPLING":
            needed_pos = len(neg_records) - len(pos_records)
            extra_pos = rng.choices(pos_records, k=max(0, needed_pos))
            resampled_records = training_records + extra_pos
            rng.shuffle(resampled_records)

        elif strategy == "SMOTE":
            # Simplified tenant-safe SMOTE interpolation for numerical fields
            needed_pos = max(0, len(neg_records) - len(pos_records))
            synthetic_records: list[dict[str, Any]] = []
            for _ in range(needed_pos):
                base_rec = rng.choice(pos_records)
                partner_rec = rng.choice(pos_records)
                syn_rec = dict(base_rec)
                # Compute linear interpolation for float/Decimal amounts
                b_amt = float(base_rec.get("amount", 0.0))
                p_amt = float(partner_rec.get("amount", 0.0))
                alpha = rng.random()
                syn_rec["amount"] = round(b_amt + alpha * (p_amt - b_amt), 2)
                syn_rec["is_synthetic"] = True
                synthetic_records.append(syn_rec)

            resampled_records = training_records + synthetic_records
            rng.shuffle(resampled_records)
        else:
            resampled_records = training_records

        final_analysis = self.analyze_distribution(resampled_records, target_column=target_column)
        updated_result = final_analysis.model_copy(
            update={
                "selected_strategy": strategy,
                "strategy_parameters": {
                    "original_total": len(training_records),
                    "resampled_total": len(resampled_records),
                },
                "training_only": True,
                "random_seed": seed,
            }
        )
        logger.info(
            "Resampled training records (%s): %d -> %d (seed=%d)",
            strategy,
            len(training_records),
            len(resampled_records),
            seed,
        )
        return resampled_records, updated_result
