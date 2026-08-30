"""Data Cleaning Pipeline (Phase 219)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.schemas.ml_cleaning import CleaningRuleAudit, DataCleaningResult, QuarantineRecord

logger = logging.getLogger("fraudguard.ml.cleaning")


class DataCleaner:
    """Production Data Cleaning Engine with transformation audits & quarantine (Phase 219)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()
        self.quarantine_vault: list[QuarantineRecord] = []

    def clean_dataset(
        self, records: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], DataCleaningResult]:
        """Perform observable data cleaning with quarantine & rule auditing (Phase 219)."""  # noqa: E501
        input_rows = len(records)
        cleaned_records: list[dict[str, Any]] = []

        seen_ids: set[str] = set()
        duplicate_rows = 0
        invalid_rows = 0
        modified_rows = 0
        quarantined_count = 0

        rule_audits: list[CleaningRuleAudit] = []

        for rec in records:
            # 1. Deduplication Rule
            tx_id = rec.get("transaction_id") or rec.get("id")
            if tx_id:
                tx_id_str = str(tx_id)
                if tx_id_str in seen_ids:
                    duplicate_rows += 1
                    raw_hash = hashlib.sha256(
                        json.dumps(str(rec), sort_keys=True).encode()
                    ).hexdigest()  # noqa: E501
                    self.quarantine_vault.append(
                        QuarantineRecord(
                            reason_code="DUPLICATE_IDENTIFIER",
                            raw_data_hash=raw_hash,
                            field_summary={"transaction_id": tx_id_str},
                        )
                    )
                    quarantined_count += 1
                    continue
                seen_ids.add(tx_id_str)

            cleaned_rec = dict(rec)
            was_modified = False

            # 2. Amount Cleaning & Range Validation Rule
            amt = cleaned_rec.get("amount")
            if amt is not None:
                try:
                    dec_amt = Decimal(str(amt))
                    if dec_amt < Decimal("0.00"):
                        invalid_rows += 1
                        raw_hash = hashlib.sha256(
                            json.dumps(str(rec), sort_keys=True).encode()
                        ).hexdigest()  # noqa: E501
                        self.quarantine_vault.append(
                            QuarantineRecord(
                                reason_code="NEGATIVE_AMOUNT",
                                raw_data_hash=raw_hash,
                                field_summary={"field": "amount", "issue": "negative"},
                            )
                        )
                        quarantined_count += 1
                        continue
                    cleaned_rec["amount"] = dec_amt
                except Exception:
                    invalid_rows += 1
                    raw_hash = hashlib.sha256(
                        json.dumps(str(rec), sort_keys=True).encode()
                    ).hexdigest()  # noqa: E501
                    self.quarantine_vault.append(
                        QuarantineRecord(
                            reason_code="UNPARSEABLE_AMOUNT",
                            raw_data_hash=raw_hash,
                            field_summary={"field": "amount", "issue": "unparseable"},
                        )
                    )
                    quarantined_count += 1
                    continue

            # 3. Currency Normalization Rule
            curr = cleaned_rec.get("currency")
            if not curr or not isinstance(curr, str):
                cleaned_rec["currency"] = "USD"
                was_modified = True
            else:
                normalized_curr = curr.strip().upper()
                if normalized_curr != curr:
                    cleaned_rec["currency"] = normalized_curr
                    was_modified = True

            # 4. Timestamp Normalization Rule
            ts = cleaned_rec.get("created_at")
            if isinstance(ts, str):
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    cleaned_rec["created_at"] = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
                except Exception:
                    cleaned_rec["created_at"] = datetime.now(UTC)
                    was_modified = True
            elif isinstance(ts, datetime):
                cleaned_rec["created_at"] = ts.replace(tzinfo=UTC) if ts.tzinfo is None else ts
            else:
                cleaned_rec["created_at"] = datetime.now(UTC)
                was_modified = True

            if was_modified:
                modified_rows += 1

            cleaned_records.append(cleaned_rec)

        clean_rows = len(cleaned_records)
        removed_rows = input_rows - clean_rows

        rule_audits.append(
            CleaningRuleAudit(
                rule_id="DUPLICATE_REMOVAL",
                category="DUPLICATE_REMOVAL",
                input_count=input_rows,
                output_count=input_rows - duplicate_rows,
                modified_count=0,
                removed_count=duplicate_rows,
                reason="Removed duplicate transaction IDs.",
            )
        )
        rule_audits.append(
            CleaningRuleAudit(
                rule_id="RANGE_AND_TYPE_VALIDATION",
                category="RANGE_VALIDATION",
                input_count=input_rows - duplicate_rows,
                output_count=clean_rows,
                modified_count=modified_rows,
                removed_count=invalid_rows,
                reason="Validated numerical ranges and timestamp types.",
            )
        )

        result_stats = DataCleaningResult(
            input_rows=input_rows,
            clean_rows=clean_rows,
            removed_rows=removed_rows,
            modified_rows=modified_rows,
            duplicate_rows=duplicate_rows,
            invalid_rows=invalid_rows,
            quarantined_rows=quarantined_count,
            rule_audits=rule_audits,
            cleaning_version="2.0",
        )

        logger.info(
            "Cleaned dataset: input=%d -> clean=%d (quarantined=%d, modified=%d)",
            input_rows,
            clean_rows,
            quarantined_count,
            modified_rows,
        )

        return cleaned_records, result_stats
