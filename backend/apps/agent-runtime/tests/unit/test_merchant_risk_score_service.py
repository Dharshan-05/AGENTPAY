"""Unit & Adversarial Tests for Merchant Risk Score Service (Phase 252)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.ml.risk.merchant_risk import MerchantRiskScoreService


def test_01_valid_merchant_signal_and_new_merchant_fallback() -> None:
    """1. Test valid merchant signal processing and new merchant cold-start handling."""
    service = MerchantRiskScoreService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    sig_data = {
        "tenant_id": str(t_id),
        "agent_id": str(a_id),
        "merchant_id": "merch_123",
        "merchant_risk_score": 30.0,
        "merchant_familiarity_score": 0.85,
        "confidence": 1.0,
        "is_new_merchant": False,
        "signal_timestamp": now.isoformat(),
    }

    res = service.process_merchant_signal(sig_data, "tx_001", now)
    assert res.merchant_risk_score == 30.0
    assert res.merchant_familiarity_score == 0.85
    assert res.is_new_merchant is False

    # New merchant cold-start fallback
    sig_data_new = {
        "tenant_id": str(t_id),
        "agent_id": str(a_id),
        "merchant_id": "merch_new_456",
        "merchant_risk_score": 0.0,
        "merchant_familiarity_score": 0.0,
        "confidence": 0.0,
        "is_new_merchant": True,
        "signal_timestamp": now.isoformat(),
    }

    res_new = service.process_merchant_signal(
        sig_data_new, "tx_002", now, fallback_new_merchant_score=50.0
    )
    assert res_new.is_new_merchant is True
    assert res_new.is_cold_start is True
    assert res_new.merchant_risk_score == 50.0  # Fallback, NOT zero risk!


def test_02_point_in_time_and_tenant_mismatch_rejection() -> None:
    """2. Mandatory Test: Rejects future timestamp and tenant mismatch."""
    service = MerchantRiskScoreService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    now = datetime.now(UTC)
    future = now + timedelta(hours=2)

    sig_future = {
        "tenant_id": str(tenant_a),
        "merchant_risk_score": 20.0,
        "signal_timestamp": future.isoformat(),
    }

    with pytest.raises(ValueError, match="Point-in-time violation"):
        service.process_merchant_signal(sig_future, "tx_fut", now)

    sig_tenant_b = {
        "tenant_id": str(tenant_b),
        "merchant_risk_score": 20.0,
        "signal_timestamp": now.isoformat(),
    }

    with pytest.raises(ValueError, match="Tenant mismatch!"):
        service.process_merchant_signal(
            sig_tenant_b, "tx_mismatch", now, expected_tenant_id=tenant_a
        )  # noqa: E501
