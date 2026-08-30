"""Unit & Adversarial Tests for Behaviour Risk Score Service (Phase 251)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.ml.risk.behaviour_risk import BehaviourRiskScoreService
from app.schemas.behaviour_risk import BehaviourRiskResult as UpstreamBehaviourRiskResult


def test_01_valid_behaviour_signal_processing_and_cold_start() -> None:
    """1. Test valid behaviour risk processing and cold start state handling."""
    service = BehaviourRiskScoreService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    upstream = UpstreamBehaviourRiskResult(
        tenant_id=t_id,
        agent_id=a_id,
        behaviour_risk_score=Decimal("45.50"),
        severity="MEDIUM",
        risk_factors=[],
        confidence=Decimal("1.00"),
        explanation="Normal behaviour pattern",
        evaluated_at=now,
    )

    res = service.process_behaviour_signal(
        upstream_signal=upstream,
        transaction_id="tx_001",
        prediction_timestamp=now,
    )

    assert res.behaviour_risk_score == 45.50
    assert res.behaviour_confidence == 1.00
    assert res.is_cold_start is False

    # Cold start handling (confidence = 0.0 or severity = COLD_START)
    upstream_cold = UpstreamBehaviourRiskResult(
        tenant_id=t_id,
        agent_id=a_id,
        behaviour_risk_score=Decimal("0.00"),
        severity="COLD_START",
        risk_factors=[],
        confidence=Decimal("0.00"),
        explanation="Insufficient history",
        evaluated_at=now,
    )

    res_cold = service.process_behaviour_signal(
        upstream_signal=upstream_cold,
        transaction_id="tx_002",
        prediction_timestamp=now,
        fallback_cold_start_score=50.0,
    )

    assert res_cold.is_cold_start is True
    assert res_cold.behaviour_risk_score == 50.0  # Fallback score, NOT false zero risk!


def test_02_adversarial_future_timestamp_and_confidence_out_of_bounds() -> None:
    """2. Mandatory Adversarial Test E & F: Future timestamp and confidence > 1.0 fail closed."""  # noqa: E501
    service = BehaviourRiskScoreService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)
    future_time = now + timedelta(hours=2)

    upstream_future = UpstreamBehaviourRiskResult(
        tenant_id=t_id,
        agent_id=a_id,
        behaviour_risk_score=Decimal("30.00"),
        severity="LOW",
        risk_factors=[],
        confidence=Decimal("1.00"),
        explanation="Future signal",
        evaluated_at=future_time,
    )

    # Future timestamp raises Point-in-Time violation
    with pytest.raises(
        ValueError, match="Point-in-time violation: behaviour signal timestamp is in the future!"
    ):  # noqa: E501
        service.process_behaviour_signal(
            upstream_signal=upstream_future,
            transaction_id="tx_future",
            prediction_timestamp=now,
        )

    # Confidence > 1.0 fails closed
    dict_signal_bad_conf = {
        "tenant_id": str(t_id),
        "agent_id": str(a_id),
        "behaviour_risk_score": 40.0,
        "confidence": 1.5,  # Out of bounds confidence!
        "evaluated_at": now,
    }

    with pytest.raises(ValueError, match="Invalid behaviour confidence value"):
        service.process_behaviour_signal(
            upstream_signal=dict_signal_bad_conf,
            transaction_id="tx_bad_conf",
            prediction_timestamp=now,
        )
