"""Benchmark dataset loader for ATIM Phase 8."""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.evaluation.models import EvaluationCase


class ATIMBenchmarkLoader:
    """Loads JSONL benchmark datasets into strongly typed EvaluationCase instances."""

    def __init__(self, dataset_dir: Path | None = None) -> None:
        if dataset_dir is None:
            # Default dataset directory inside tests/evaluation/datasets/
            self.dataset_dir = Path(__file__).parents[3] / "tests" / "evaluation" / "datasets"
        else:
            self.dataset_dir = dataset_dir

    def load_dataset(self, filename: str) -> list[EvaluationCase]:
        """Read JSONL file and parse into list of EvaluationCase models."""
        file_path = self.dataset_dir / filename
        if not file_path.exists():
            return []

        cases: list[EvaluationCase] = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    continue
                data = json.loads(line_str)
                cases.append(EvaluationCase(**data))
        return cases
