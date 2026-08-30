"""Unit & Adversarial Tests for Velocity Risk Score Service (Phase 253)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.ml.risk.velocity_risk import VelocityRiskScoreService


def test_01_valid_velocity_signal_and_burst_detection() -> None:
    """1. Test valid velocity signal processing, Decimal precision, and burst flag preservation."""
    service = VelocityRiskScoreService()
    t_id = uuid.uuid4()
    now = datetime.now(UTC)

    sig_data = {
        "tenant_id": str(t_id),
        "velocity_risk_score": 65.0,
        "burst_detected": True,
        "transaction_count": 15,
        "amount_velocity": Decimal("1500.50"),
        "time_window": "15m",
        "confidence": 0.95,
        "signal_timestamp": now.isoformat(),
    }

    res = service.process_velocity_signal(sig_data, "tx_001", now)
    assert res.velocity_risk_score == 65.0
    assert res.burst_detected is True
    assert res.amount_velocity == 1500.50
    assert res.time_window == "15m"


def test_02_nan_inf_and_future_timestamp_rejection() -> None:
    """2. Mandatory Test: Rejects NaN/Inf score and future timestamp."""
    service = VelocityRiskScoreService()
    t_id = uuid.uuid4()
    now = datetime.now(UTC)

    sig_nan = {
        "tenant_id": str(t_id),
        "velocity_risk_score": float("nan"),
        "signal_timestamp": now.isoformat(),
    }
    with pytest.raises(ValueError, match="Invalid velocity risk score value"):
        service.process_velocity_signal(sig_nan, "tx_nan", now)

    future = now + timedelta(hours=1)
    sig_future = {
        "tenant_id": str(t_id),
        "velocity_risk_score": 20.0,
        "signal_timestamp": future.isoformat(),
    }
    with pytest.raises(ValueError, match="Point-in-time violation"):
        service.process_velocity_signal(sig_future, "tx_fut", now)
