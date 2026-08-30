"""Unit & Adversarial Tests for Intent Risk Score Service (Phase 254)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.ml.risk.intent_risk import IntentRiskScoreService


def test_01_valid_intent_signal_and_missing_data_fallback() -> None:
    """1. Test valid intent signal processing and missing intent fallback score."""
    service = IntentRiskScoreService()
    t_id = uuid.uuid4()
    now = datetime.now(UTC)

    sig_data = {
        "tenant_id": str(t_id),
        "intent_risk_score": 15.0,
        "intent_confidence": 1.0,
        "intent_can_proceed": True,
        "intent_decision": "VERIFIED",
        "signal_timestamp": now.isoformat(),
    }

    res = service.process_intent_signal(sig_data, "tx_001", now)
    assert res.intent_risk_score == 15.0
    assert res.intent_can_proceed is True
    assert res.is_available is True

    # Missing intent data fallback check (is_available = False, fallback score 50.0)
    res_missing = service.process_intent_signal(
        signal_data=None,
        transaction_id="tx_missing",
        prediction_timestamp=now,
        expected_tenant_id=t_id,
        fallback_unavailable_score=50.0,
    )
    assert res_missing.is_available is False
    assert res_missing.intent_risk_score == 50.0  # NOT zero risk!


def test_02_can_proceed_does_not_override_policy() -> None:
    """2. Mandatory Security Test: intent_can_proceed=True is NOT a fraud safety override."""
    service = IntentRiskScoreService()
    t_id = uuid.uuid4()
    now = datetime.now(UTC)

    sig_proceed_high_risk = {
        "tenant_id": str(t_id),
        "intent_risk_score": 90.0,
        "intent_confidence": 1.0,
        "intent_can_proceed": True,  # Upstream intent verification can proceed
        "intent_decision": "VERIFIED_HIGH_RISK",
        "signal_timestamp": now.isoformat(),
    }

    res = service.process_intent_signal(sig_proceed_high_risk, "tx_high_risk", now)
    assert res.intent_risk_score == 90.0
    assert res.intent_can_proceed is True
    # Verify score remains high (90.0) despite intent_can_proceed=True!
