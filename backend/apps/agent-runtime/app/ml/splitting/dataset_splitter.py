"""Dataset Partitioning & Splitting Framework (Phase 233)."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.dataset.training_dataset_builder import TrainingDataset
from app.schemas.ml_training import SplitManifest, TrainingDatasetManifest

logger = logging.getLogger("fraudguard.ml.splitting")


@dataclass
class DatasetSplits:
    """Container holding partitioned train, validation, and test datasets with manifest (Phase 233)."""  # noqa: E501

    train_dataset: TrainingDataset
    validation_dataset: TrainingDataset
    test_dataset: TrainingDataset
    split_manifest: SplitManifest


class DatasetSplitter:
    """Production Dataset Splitting Engine (Phase 233)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()

    def split_dataset(
        self,
        dataset: TrainingDataset,
        strategy: str = "TEMPORAL",
        train_ratio: float = 0.70,
        validation_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_seed: int | None = None,
    ) -> DatasetSplits:
        """Partition training dataset into train, validation, and test splits (Phase 233)."""
        total_ratio = train_ratio + validation_ratio + test_ratio
        if abs(total_ratio - 1.0) > 1e-4:
            raise ValueError(f"Split ratios must sum to 1.0 (got {total_ratio:.4f})")

        total_samples = len(dataset.X)
        if total_samples < 3:
            raise ValueError(
                f"Dataset has insufficient samples ({total_samples}) to split into 3 partitions."
            )  # noqa: E501

        seed = random_seed if random_seed is not None else self.config.random_seed
        rng = random.Random(seed)

        # Pair records with labels for consistent indexing
        paired_data = list(zip(dataset.X, dataset.y, strict=True))

        train_pairs: list[tuple[dict[str, Any], int]] = []
        val_pairs: list[tuple[dict[str, Any], int]] = []
        test_pairs: list[tuple[dict[str, Any], int]] = []

        temporal_boundaries: dict[str, str] = {}

        if strategy == "TEMPORAL":
            # Sort chronologically by created_at
            def get_ts(item: tuple[dict[str, Any], int]) -> datetime:
                ts = item[0].get("created_at")
                if isinstance(ts, datetime):
                    return ts.replace(tzinfo=UTC) if ts.tzinfo is None else ts
                if isinstance(ts, str):
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
                    except Exception:
                        pass
                return datetime.now(UTC)

            sorted_data = sorted(paired_data, key=get_ts)

            train_end = int(total_samples * train_ratio)
            val_end = train_end + int(total_samples * validation_ratio)

            train_pairs = sorted_data[:train_end]
            val_pairs = sorted_data[train_end:val_end]
            test_pairs = sorted_data[val_end:]

            if train_pairs:
                temporal_boundaries["train_max"] = get_ts(train_pairs[-1]).isoformat()
            if val_pairs:
                temporal_boundaries["val_min"] = get_ts(val_pairs[0]).isoformat()
                temporal_boundaries["val_max"] = get_ts(val_pairs[-1]).isoformat()
            if test_pairs:
                temporal_boundaries["test_min"] = get_ts(test_pairs[0]).isoformat()

        elif strategy == "STRATIFIED":
            pos_pairs = [p for p in paired_data if p[1] == 1]
            neg_pairs = [p for p in paired_data if p[1] == 0]

            rng.shuffle(pos_pairs)
            rng.shuffle(neg_pairs)

            def partition_list(
                items: list[tuple[dict[str, Any], int]],
            ) -> tuple[
                list[tuple[dict[str, Any], int]],
                list[tuple[dict[str, Any], int]],
                list[tuple[dict[str, Any], int]],
            ]:
                n = len(items)
                tr_end = int(n * train_ratio)
                va_end = tr_end + int(n * validation_ratio)
                return items[:tr_end], items[tr_end:va_end], items[va_end:]

            tr_pos, va_pos, te_pos = partition_list(pos_pairs)
            tr_neg, va_neg, te_neg = partition_list(neg_pairs)

            train_pairs = tr_pos + tr_neg
            val_pairs = va_pos + va_neg
            test_pairs = te_pos + te_neg

            rng.shuffle(train_pairs)
            rng.shuffle(val_pairs)
            rng.shuffle(test_pairs)

        elif strategy == "RANDOM":
            shuffled = list(paired_data)
            rng.shuffle(shuffled)

            train_end = int(total_samples * train_ratio)
            val_end = train_end + int(total_samples * validation_ratio)

            train_pairs = shuffled[:train_end]
            val_pairs = shuffled[train_end:val_end]
            test_pairs = shuffled[val_end:]
        else:
            raise ValueError(
                f"Unknown split strategy '{strategy}'. Allowed: TEMPORAL, STRATIFIED, RANDOM"
            )  # noqa: E501

        # Assert Disjointness using transaction_id if present
        train_ids = {
            p[0].get("transaction_id") or p[0].get("id")
            for p in train_pairs
            if p[0].get("transaction_id") or p[0].get("id")
        }  # noqa: E501
        val_ids = {
            p[0].get("transaction_id") or p[0].get("id")
            for p in val_pairs
            if p[0].get("transaction_id") or p[0].get("id")
        }  # noqa: E501
        test_ids = {
            p[0].get("transaction_id") or p[0].get("id")
            for p in test_pairs
            if p[0].get("transaction_id") or p[0].get("id")
        }  # noqa: E501

        if train_ids and val_ids and (train_ids & val_ids):
            raise RuntimeError(
                "Disjointness failure: Overlap detected between train and validation partitions!"
            )  # noqa: E501
        if train_ids and test_ids and (train_ids & test_ids):
            raise RuntimeError(
                "Disjointness failure: Overlap detected between train and test partitions!"
            )  # noqa: E501
        if val_ids and test_ids and (val_ids & test_ids):
            raise RuntimeError(
                "Disjointness failure: Overlap detected between validation and test partitions!"
            )  # noqa: E501

        def build_partition_dataset(
            pairs: list[tuple[dict[str, Any], int]], partition_name: str
        ) -> TrainingDataset:
            X_part = [p[0] for p in pairs]
            y_part = [p[1] for p in pairs]
            manifest_part = TrainingDatasetManifest(
                dataset_version=f"{dataset.manifest.dataset_version}-{partition_name}",
                dataset_fingerprint=dataset.manifest.dataset_fingerprint,
                feature_versions=dataset.manifest.feature_versions,
                target_definition=dataset.target_name,
                row_count=len(X_part),
                feature_count=len(dataset.feature_names),
                tenant_id=dataset.manifest.tenant_id,
            )
            return TrainingDataset(
                X=X_part,
                y=y_part,
                feature_names=dataset.feature_names,
                target_name=dataset.target_name,
                manifest=manifest_part,
            )

        train_ds = build_partition_dataset(train_pairs, "train")
        val_ds = build_partition_dataset(val_pairs, "val")
        test_ds = build_partition_dataset(test_pairs, "test")

        class_distribs = {
            "train": {"0": train_ds.y.count(0), "1": train_ds.y.count(1)},
            "validation": {"0": val_ds.y.count(0), "1": val_ds.y.count(1)},
            "test": {"0": test_ds.y.count(0), "1": test_ds.y.count(1)},
        }

        split_manifest = SplitManifest(
            strategy=strategy,
            random_seed=seed,
            train_count=len(train_ds.X),
            validation_count=len(val_ds.X),
            test_count=len(test_ds.X),
            train_ratio=round(len(train_ds.X) / total_samples, 4),
            validation_ratio=round(len(val_ds.X) / total_samples, 4),
            test_ratio=round(len(test_ds.X) / total_samples, 4),
            temporal_boundaries=temporal_boundaries,
            class_distributions=class_distribs,
            dataset_fingerprint=dataset.manifest.dataset_fingerprint,
        )

        logger.info(
            "Split dataset (%s): train=%d, val=%d, test=%d (fingerprint=%s)",
            strategy,
            len(train_ds.X),
            len(val_ds.X),
            len(test_ds.X),
            dataset.manifest.dataset_fingerprint,
        )

        return DatasetSplits(
            train_dataset=train_ds,
            validation_dataset=val_ds,
            test_dataset=test_ds,
            split_manifest=split_manifest,
        )
