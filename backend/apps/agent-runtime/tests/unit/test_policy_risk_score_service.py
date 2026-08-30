"""Unit & Security Precedence Tests for Policy Risk Score Service (Phase 255)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.ml.risk.policy_risk import PolicyRiskScoreService
from app.schemas.policy_evaluation import PolicyEvaluationResult


def test_01_policy_deny_precedence_and_allow_ml_scoring_flag() -> None:
    """1. Mandatory Security Test: Policy DENY sets policy_risk_score=100.0 and allow_ml_scoring=False."""  # noqa: E501
    service = PolicyRiskScoreService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    policy_deny_res = PolicyEvaluationResult(
        tenant_id=t_id,
        agent_id=a_id,
        decision="DENY",
        reason_codes=["SPENDING_LIMIT_EXCEEDED"],
        decision_reason="Daily limit exceeded",
        evaluated_at=now,
    )

    res_deny = service.process_policy_signal(policy_deny_res, "tx_deny", now)
    assert res_deny.policy_risk_score == 100.0
    assert res_deny.policy_decision == "DENY"
    assert res_deny.authoritative is True
    assert res_deny.allow_ml_scoring is False  # FORBIDS downstream ML authorization override!

    policy_allow_res = PolicyEvaluationResult(
        tenant_id=t_id,
        agent_id=a_id,
        decision="ALLOW",
        reason_codes=["POLICY_PASS"],
        decision_reason="Policy passed",
        evaluated_at=now,
    )

    res_allow = service.process_policy_signal(policy_allow_res, "tx_allow", now)
    assert res_allow.policy_risk_score == 0.0
    assert res_allow.policy_decision == "ALLOW"
    assert res_allow.allow_ml_scoring is True


def test_02_unknown_policy_decision_fails_closed() -> None:
    """2. Mandatory Security Test: UNKNOWN policy decision fails closed."""
    service = PolicyRiskScoreService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    dict_unknown = {
        "tenant_id": str(t_id),
        "agent_id": str(a_id),
        "decision": "UNKNOWN",
        "evaluated_at": now.isoformat(),
    }

    with pytest.raises(ValueError, match="Policy decision is UNKNOWN or unverified!"):
        service.process_policy_signal(dict_unknown, "tx_unk", now)
