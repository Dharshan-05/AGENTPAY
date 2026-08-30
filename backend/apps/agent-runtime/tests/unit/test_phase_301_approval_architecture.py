import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.schemas.payment import SupportedCurrency
from app.schemas.payment_approval import (
    ApprovalDecisionRecord,
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatus,
)
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str,
    decision: FinalRiskDecision = FinalRiskDecision.ALLOW,
    score: float = 10.0,
) -> FinalRiskDecisionResult:
    band = RiskThresholdBand.LOW_RISK_BAND if score <= 30 else RiskThresholdBand.HIGH_RISK_BAND
    return FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        prediction_timestamp=datetime.now(UTC),
        decision=decision,
        decision_reason="TEST_EVALUATION",
        composite_risk_score=score,
        risk_band=band,
        policy_precedence="ALLOW" if decision == FinalRiskDecision.ALLOW else "REVIEW",
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
        source_fingerprints=["s" * 64],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="fp_dec_301",
        created_at=datetime.now(UTC),
    )


def test_01_low_risk_low_value_not_required() -> None:
    """1. Test low risk score and low value results in NOT_REQUIRED approval status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_appr_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id, score=15.0)

    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    assert req.approval_status == ApprovalStatus.NOT_REQUIRED
    assert engine.is_execution_permitted(req) is True


def test_02_high_risk_score_requires_pending_approval() -> None:
    """2. Test high risk score (> 30.0) evaluates to PENDING approval status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_appr_02"
    decision = _make_decision_result(tenant_id, agent_id, tx_id, score=45.0)

    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
    )

    assert req.approval_status == ApprovalStatus.PENDING
    assert engine.is_execution_permitted(req) is False


def test_03_high_value_requires_pending_approval() -> None:
    """3. Test high monetary value (> 50,000 INR) evaluates to PENDING approval status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_appr_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id, score=10.0)

    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("75000.00"),  # High value!
        currency=SupportedCurrency.INR,
    )

    assert req.approval_status == ApprovalStatus.PENDING
    assert engine.is_execution_permitted(req) is False


def test_04_review_decision_requires_pending_approval() -> None:
    """4. Test REVIEW risk decision evaluates to PENDING approval status."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_appr_04"
    decision = _make_decision_result(
        tenant_id, agent_id, tx_id, decision=FinalRiskDecision.REVIEW, score=10.0
    )

    engine = ApprovalPolicyEngine()
    req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("50.00"),
        currency=SupportedCurrency.INR,
    )

    assert req.approval_status == ApprovalStatus.PENDING
    assert engine.is_execution_permitted(req) is False


def test_05_critical_invariant_agent_cannot_create_approved_request() -> None:
    """5. Critical Security Invariant: ApprovalRequest CANNOT be initialized as APPROVED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    with pytest.raises(ValueError) as exc_info:
        ApprovalRequest(
            approval_id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id="tx_05",
            approval_status=ApprovalStatus.APPROVED,  # Self-approval attempt!
            risk_score=10.0,
            amount=Decimal("100.00"),
            currency=SupportedCurrency.INR,
            approval_fingerprint="fp_05",
        )

    assert "Agent requests CANNOT set approval_status to APPROVED" in str(exc_info.value)


def test_06_critical_invariant_reviewer_cannot_be_agent() -> None:
    """6. Critical Security Invariant: ApprovalDecisionRecord reviewer_id cannot be an agent."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    approval_id = uuid.uuid4()

    for forbidden_reviewer in ["agent", "bot", "automated", "self", "system"]:
        with pytest.raises(ValueError) as exc_info:
            ApprovalDecisionRecord(
                approval_id=approval_id,
                tenant_id=tenant_id,
                agent_id=agent_id,
                transaction_id="tx_06",
                reviewer_id=forbidden_reviewer,
                decision_status=ApprovalStatus.APPROVED,
                decision_reason="Agent approved itself",
                decision_fingerprint="fp_06",
            )
        assert "Reviewer ID cannot be an automated agent" in str(exc_info.value)


def test_07_execution_permitted_for_valid_human_approval() -> None:
    """7. Test is_execution_permitted returns True for valid human reviewer decision."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    tx_id = "tx_appr_07"

    req = ApprovalRequest(
        approval_id=approval_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        approval_status=ApprovalStatus.PENDING,
        risk_score=50.0,
        amount=Decimal("100000.00"),
        currency=SupportedCurrency.INR,
        approval_fingerprint="fp_req_07",
    )

    decision_record = ApprovalDecisionRecord(
        approval_id=approval_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        reviewer_id="human_compliance_officer_42",
        decision_status=ApprovalStatus.APPROVED,
        decision_reason="Approved after manual compliance verification",
        decision_fingerprint="fp_dec_07",
    )

    engine = ApprovalPolicyEngine()
    assert engine.is_execution_permitted(req, decision_record) is True


def test_08_execution_blocked_for_rejected_approval() -> None:
    """8. Test is_execution_permitted returns False when reviewer rejected payment."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    tx_id = "tx_appr_08"

    req = ApprovalRequest(
        approval_id=approval_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        approval_status=ApprovalStatus.PENDING,
        risk_score=50.0,
        amount=Decimal("100000.00"),
        currency=SupportedCurrency.INR,
        approval_fingerprint="fp_req_08",
    )

    decision_record = ApprovalDecisionRecord(
        approval_id=approval_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        reviewer_id="human_compliance_officer_42",
        decision_status=ApprovalStatus.REJECTED,
        decision_reason="High risk transaction rejected",
        decision_fingerprint="fp_dec_08",
    )

    engine = ApprovalPolicyEngine()
    assert engine.is_execution_permitted(req, decision_record) is False


def test_09_approval_fingerprint_sha256_length() -> None:
    """9. Security Test: Approval request fingerprint is valid 64-character SHA-256."""
    engine = ApprovalPolicyEngine()
    fp = engine.calculate_approval_fingerprint(
        approval_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_09",
        status=ApprovalStatus.PENDING,
        risk_score=25.0,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        policy_version="1.0.0",
    )
    assert len(fp) == 64


def test_10_approval_schemas_forbid_extra_fields() -> None:
    """10. Security Test: Approval Pydantic models forbid extra injected fields."""
    with pytest.raises(ValueError):
        ApprovalPolicy.model_validate({"policy_version": "1.0.0", "injected_param": 123})


def test_11_static_check_no_direct_razorpay_sdk_imports() -> None:
    """11. Static Check: ApprovalPolicyEngine DOES NOT import razorpay SDK directly."""
    import app.payment.approval.approval_policy_engine as ape_mod

    source_code = inspect.getsource(ape_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code
