"""Transaction Feature Pipeline (Phase 222)."""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.ml.features.base import FeatureCategory, FeatureDefinition, FeatureType, FeatureValue

logger = logging.getLogger("fraudguard.ml.features.transaction")

DEF_TX_AMOUNT = FeatureDefinition(
    name="tx_amount",
    feature_type=FeatureType.NUMERIC,
    source="PAYMENT_ORDER",
    category=FeatureCategory.TRANSACTION,
    transformation_description="Raw transaction amount in Decimal",
    version="1.0.0",
)

DEF_TX_AMOUNT_LOG = FeatureDefinition(
    name="tx_amount_log",
    feature_type=FeatureType.NUMERIC,
    source="PAYMENT_ORDER",
    category=FeatureCategory.TRANSACTION,
    transformation_description="Natural log of (amount + 1.0)",
    version="1.0.0",
)

DEF_IS_NIGHT_TX = FeatureDefinition(
    name="is_night_tx",
    feature_type=FeatureType.BOOLEAN,
    source="PAYMENT_ORDER",
    category=FeatureCategory.TRANSACTION,
    transformation_description="True if transaction created between 23:00 and 05:00 UTC",
    version="1.0.0",
)

DEF_IS_WEEKEND_TX = FeatureDefinition(
    name="is_weekend_tx",
    feature_type=FeatureType.BOOLEAN,
    source="PAYMENT_ORDER",
    category=FeatureCategory.TRANSACTION,
    transformation_description="True if transaction created on Saturday or Sunday",
    version="1.0.0",
)

DEF_POINT_IN_TIME_VALID = FeatureDefinition(
    name="point_in_time_valid",
    feature_type=FeatureType.BOOLEAN,
    source="PAYMENT_ORDER",
    category=FeatureCategory.TRANSACTION,
    transformation_description="True if transaction timestamp <= prediction timestamp (leakage-safe)",  # noqa: E501
    version="1.0.0",
)


class TransactionFeatureExtractor:
    """Production Point-in-Time Correct Transaction Feature Extractor (Phase 222)."""

    def extract_features(
        self, record: dict[str, Any], prediction_timestamp: datetime | None = None
    ) -> list[FeatureValue]:
        """Extract transaction ML features with point-in-time correctness (Phase 222)."""
        tenant_id = str(record.get("tenant_id", "UNKNOWN"))
        agent_id = str(record["agent_id"]) if record.get("agent_id") else None

        amt = record.get("amount")
        dec_amt = Decimal(str(amt)) if amt is not None else Decimal("0.00")
        float_amt = float(dec_amt)

        ts = record.get("created_at")
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now(UTC)
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now(UTC)

        pred_ts = prediction_timestamp or datetime.now(UTC)
        is_pit_valid = dt.replace(tzinfo=UTC) <= pred_ts.replace(tzinfo=UTC)

        is_night = dt.hour >= 23 or dt.hour <= 5
        is_weekend = dt.weekday() >= 5

        return [
            FeatureValue(
                definition=DEF_TX_AMOUNT,
                value=dec_amt,
                tenant_id=tenant_id,
                agent_id=agent_id,
            ),
            FeatureValue(
                definition=DEF_TX_AMOUNT_LOG,
                value=round(math.log(float_amt + 1.0), 4),
                tenant_id=tenant_id,
                agent_id=agent_id,
            ),
            FeatureValue(
                definition=DEF_IS_NIGHT_TX,
                value=is_night,
                tenant_id=tenant_id,
                agent_id=agent_id,
            ),
            FeatureValue(
                definition=DEF_IS_WEEKEND_TX,
                value=is_weekend,
                tenant_id=tenant_id,
                agent_id=agent_id,
            ),
            FeatureValue(
                definition=DEF_POINT_IN_TIME_VALID,
                value=is_pit_valid,
                tenant_id=tenant_id,
                agent_id=agent_id,
            ),
        ]
