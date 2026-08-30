"""Unit tests for Feature Store Management (Phase 230)."""

from __future__ import annotations

import pytest

from app.ml.feature_store.feature_store import FeatureStore
from app.ml.features.base import (  # noqa: E501
    FeatureCategory,
    FeatureDefinition,
    FeatureSecurityClassification,
    FeatureType,
)


def test_01_feature_store_lifecycle_lineage_and_transition_guard() -> None:
    """1. Test FeatureStore registration, lifecycle transition validation, lineage, and catalog export."""  # noqa: E501
    fs = FeatureStore()
    fdef = FeatureDefinition(
        name="tx_amount_log",
        feature_type=FeatureType.NUMERIC,
        source="PAYMENT_ORDER",
        category=FeatureCategory.TRANSACTION,
        security_classification=FeatureSecurityClassification.INTERNAL,
        transformation_description="Log amount",
    )

    rec = fs.register_feature(fdef, status="ACTIVE")
    assert rec.name == "tx_amount_log"
    assert rec.feature_id == "tx_amount_log:1.0.0"
    assert rec.status == "ACTIVE"

    updated = fs.update_feature_status("tx_amount_log", "DEPRECATED", version="1.0.0")
    assert updated.status == "DEPRECATED"

    # Transition validation: RETIRED -> ACTIVE must raise ValueError
    fs.update_feature_status("tx_amount_log", "RETIRED", version="1.0.0")
    with pytest.raises(ValueError, match="Cannot directly activate RETIRED feature"):
        fs.update_feature_status("tx_amount_log", "ACTIVE", version="1.0.0")

    catalog = fs.export_catalog()
    assert catalog["total_features"] == 1
    assert catalog["active_features"] == 0
    assert "tx_amount_log" in catalog["lineage_nodes"]
