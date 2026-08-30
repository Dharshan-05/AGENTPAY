"""Unit & Security Tests for Decision Audit Event Engine (Phase 283)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.risk.audit.decision_audit import DecisionAuditEventService
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def test_01_record_append_only_decision_audit_event() -> None:
    """1. Test recording an append-only DecisionAuditEvent."""
    service = DecisionAuditEventService()
    dec_res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_audit_01",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=[],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    event = service.record_decision_event(dec_res)

    assert event.decision_id == dec_res.decision_id
    assert event.decision == FinalRiskDecision.ALLOW
    assert len(event.audit_fingerprint) == 64
    assert len(service.list_events()) == 1


def test_02_audit_event_immutability() -> None:
    """2. Mandatory Security Test: DecisionAuditEvent is immutable (frozen=True)."""
    service = DecisionAuditEventService()
    dec_res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_audit_02",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=10.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=[],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    event = service.record_decision_event(dec_res)

    with pytest.raises(ValidationError, match="Instance is frozen"):
        event.reason_code = "TAMPERED_REASON"  # Attempted mutation!
