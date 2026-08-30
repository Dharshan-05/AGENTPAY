"""Dataset Validation Layer (Phase 218)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.schemas.ml_foundation import DatasetValidationResult, DatasetValidationViolation

logger = logging.getLogger("fraudguard.ml.validation")


class DatasetValidator:
    """Production Dataset Validation Engine (Phase 218)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()

    def validate_dataset(
        self,
        dataset_name: str,
        records: list[dict[str, Any]],
        required_columns: list[str] | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> DatasetValidationResult:
        """Validate dataset schema, completeness, integrity, temporal alignment, and quality score (Phase 218)."""  # noqa: E501
        cols = required_columns or ["transaction_id", "tenant_id", "amount", "currency"]
        violations: list[DatasetValidationViolation] = []

        if not records:
            violations.append(
                DatasetValidationViolation(
                    code="EMPTY_DATASET",
                    message="Dataset contains 0 records.",
                    severity="ERROR",
                )
            )
            return DatasetValidationResult(
                valid=False,
                dataset_name=dataset_name,
                dataset_version=self.config.dataset_version,
                schema_version=self.config.schema_version,
                row_count=0,
                invalid_row_count=0,
                duplicate_count=0,
                quality_score=Decimal("0.00"),
                quality_dimensions={
                    "completeness": Decimal("0.00"),
                    "schema_quality": Decimal("0.00"),
                },  # noqa: E501
                violations=violations,
            )

        row_count = len(records)
        invalid_row_count = 0
        missing_summary: dict[str, int] = {c: 0 for c in cols}
        seen_ids: set[str] = set()
        duplicate_count = 0

        amounts: list[float] = []
        now_utc = datetime.now(UTC)
        future_timestamp_count = 0

        for idx, rec in enumerate(records):
            is_row_valid = True

            # 1. Tenant boundary check
            if tenant_id and rec.get("tenant_id") and str(rec["tenant_id"]) != str(tenant_id):
                violations.append(
                    DatasetValidationViolation(
                        code="CROSS_TENANT_LEAK",
                        field_name="tenant_id",
                        message=f"Row {idx} tenant {rec.get('tenant_id')} mismatches target tenant {tenant_id}",  # noqa: E501
                        severity="FATAL",
                    )
                )
                is_row_valid = False

            # 2. Required columns & null check
            for c in cols:
                val = rec.get(c)
                if val is None or val == "":
                    missing_summary[c] = missing_summary.get(c, 0) + 1
                    is_row_valid = False

            # 3. ID uniqueness check
            tx_id = rec.get("transaction_id") or rec.get("id")
            if tx_id:
                tx_id_str = str(tx_id)
                if tx_id_str in seen_ids:
                    duplicate_count += 1
                else:
                    seen_ids.add(tx_id_str)

            # 4. Temporal validation (future timestamp check)
            ts = rec.get("created_at")
            if ts:
                try:
                    if isinstance(ts, str):
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    elif isinstance(ts, datetime):
                        dt = ts
                    else:
                        dt = None

                    if dt and dt.replace(tzinfo=UTC) > now_utc:
                        future_timestamp_count += 1
                        is_row_valid = False
                except Exception:
                    pass

            # 5. Amount validation
            amt = rec.get("amount")
            if amt is not None:
                try:
                    dec_amt = Decimal(str(amt))
                    if dec_amt < Decimal("0.00"):
                        violations.append(
                            DatasetValidationViolation(
                                code="NEGATIVE_AMOUNT",
                                field_name="amount",
                                message=f"Row {idx} has negative amount: {amt}",
                                severity="ERROR",
                            )
                        )
                        is_row_valid = False
                    else:
                        amounts.append(float(dec_amt))
                except Exception:
                    violations.append(
                        DatasetValidationViolation(
                            code="INVALID_AMOUNT_FORMAT",
                            field_name="amount",
                            message=f"Row {idx} has unparseable amount: {amt}",
                            severity="ERROR",
                        )
                    )
                    is_row_valid = False

            if not is_row_valid:
                invalid_row_count += 1

        if duplicate_count > 0:
            violations.append(
                DatasetValidationViolation(
                    code="DUPLICATE_RECORDS",
                    message=f"Found {duplicate_count} duplicate record IDs.",
                    severity="WARNING",
                )
            )

        if future_timestamp_count > 0:
            violations.append(
                DatasetValidationViolation(
                    code="FUTURE_TIMESTAMPS_DETECTED",
                    message=f"Found {future_timestamp_count} records with future timestamps relative to UTC prediction time.",  # noqa: E501
                    severity="ERROR",
                )
            )

        for col, m_cnt in missing_summary.items():
            m_ratio = m_cnt / row_count
            if m_ratio > self.config.max_missing_ratio_threshold:
                violations.append(
                    DatasetValidationViolation(
                        code="HIGH_MISSING_RATIO",
                        field_name=col,
                        message=f"Column '{col}' has missing ratio {m_ratio:.2f} > threshold {self.config.max_missing_ratio_threshold}",  # noqa: E501
                        severity="ERROR",
                    )
                )

        distribution_summary: dict[str, Any] = {}
        if amounts:
            distribution_summary["amount_min"] = round(min(amounts), 2)
            distribution_summary["amount_max"] = round(max(amounts), 2)
            distribution_summary["amount_mean"] = round(sum(amounts) / len(amounts), 2)

        # Dataset Quality Score computation (0.00 to 1.00)
        schema_q = (
            Decimal("1.00")
            if not any(v.code in ("CROSS_TENANT_LEAK", "INVALID_AMOUNT_FORMAT") for v in violations)
            else Decimal("0.00")
        )  # noqa: E501
        valid_ratio = Decimal(str(round(max(0, row_count - invalid_row_count) / row_count, 2)))
        dup_deduction = Decimal("0.20") if duplicate_count > 0 else Decimal("0.00")
        quality_score = (
            max(Decimal("0.00"), valid_ratio - dup_deduction)
            if schema_q > Decimal("0.00")
            else Decimal("0.00")
        )  # noqa: E501

        quality_dimensions = {
            "schema_quality": schema_q,
            "completeness": valid_ratio,
            "uniqueness": Decimal("1.00") - dup_deduction,
            "temporal_integrity": Decimal("1.00")
            if future_timestamp_count == 0
            else Decimal("0.50"),  # noqa: E501
        }

        has_fatal_or_error = any(v.severity in ("ERROR", "FATAL") for v in violations)
        is_valid = not has_fatal_or_error

        return DatasetValidationResult(
            valid=is_valid,
            dataset_name=dataset_name,
            dataset_version=self.config.dataset_version,
            schema_version=self.config.schema_version,
            row_count=row_count,
            invalid_row_count=invalid_row_count,
            duplicate_count=duplicate_count,
            quality_score=quality_score,
            quality_dimensions=quality_dimensions,
            missing_value_summary=missing_summary,
            distribution_summary=distribution_summary,
            violations=violations,
        )
