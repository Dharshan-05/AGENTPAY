"""Unit, Security & Adversarial Tests for Phase 302 — Approval Request Engine."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import (
    ApprovalRequestConflictError,
    ApprovalRequestService,
    ApprovalRequestServiceError,
)
from app.schemas.approval_request import (
    ApprovalRequestCreateResult,
    ApprovalRequestPriority,
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.payment_approval import ApprovalRequest, ApprovalStatus
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def _make_decision_result(
    tenant_id: uuid.UUID,
    agent_id: uuid.UUID,
    tx_id: str,
    score: float = 45.0,
) -> FinalRiskDecisionResult:
    return FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id=tx_id,
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.REVIEW,
        decision_reason="HIGH_RISK_REVIEW",
        composite_risk_score=score,
        risk_band=RiskThresholdBand.HIGH_RISK_BAND,
        policy_precedence="REVIEW",
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
        decision_fingerprint="fp_dec_302",
        created_at=datetime.now(UTC),
    )


def test_01_valid_approval_request_creation() -> None:
    """1. Test valid approval request creation produces a PENDING record."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("15000.00"),
        currency=SupportedCurrency.INR,
    )

    svc = ApprovalRequestService()
    res = svc.create_approval_request(
        decision_result=decision,
        approval_request=policy_req,
        idempotency_key="idemp_req_01",
        operation="create_order",
    )

    assert isinstance(res, ApprovalRequestCreateResult)
    assert res.is_existing is False
    assert res.request_record.status == ApprovalRequestStatus.PENDING
    assert res.request_record.tenant_id == tenant_id
    assert res.request_record.agent_id == agent_id
    assert res.request_record.transaction_id == tx_id
    assert len(res.creation_fingerprint) == 64


def test_02_tenant_mismatch_rejection() -> None:
    """2. Security Test: Mismatched tenant_id between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_02"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    policy_req = ApprovalRequest(
        approval_id=uuid.uuid4(),
        tenant_id=other_tenant,  # Spoofed tenant!
        agent_id=agent_id,
        transaction_id=tx_id,
        approval_status=ApprovalStatus.PENDING,
        risk_score=45.0,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        approval_fingerprint="fp_02",
    )

    svc = ApprovalRequestService()
    with pytest.raises(ApprovalRequestServiceError) as exc_info:
        svc.create_approval_request(decision, policy_req, idempotency_key="idemp_02")

    assert exc_info.value.error_code == "TENANT_MISMATCH"


def test_03_agent_mismatch_rejection() -> None:
    """3. Security Test: Mismatched agent_id between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    other_agent = uuid.uuid4()
    tx_id = "tx_req_03"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    policy_req = ApprovalRequest(
        approval_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=other_agent,  # Spoofed agent!
        transaction_id=tx_id,
        approval_status=ApprovalStatus.PENDING,
        risk_score=45.0,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        approval_fingerprint="fp_03",
    )

    svc = ApprovalRequestService()
    with pytest.raises(ApprovalRequestServiceError) as exc_info:
        svc.create_approval_request(decision, policy_req, idempotency_key="idemp_03")

    assert exc_info.value.error_code == "AGENT_MISMATCH"


def test_04_transaction_mismatch_rejection() -> None:
    """4. Security Test: Mismatched transaction_id between decision and request is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_04"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    policy_req = ApprovalRequest(
        approval_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="other_tx_99",  # Spoofed tx!
        approval_status=ApprovalStatus.PENDING,
        risk_score=45.0,
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        approval_fingerprint="fp_04",
    )

    svc = ApprovalRequestService()
    with pytest.raises(ApprovalRequestServiceError) as exc_info:
        svc.create_approval_request(decision, policy_req, idempotency_key="idemp_04")

    assert exc_info.value.error_code == "TRANSACTION_MISMATCH"


def test_05_invalid_initial_status_rejection() -> None:
    """5. Critical Invariant: Request with non-PENDING approval_status is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_05"

    # Creating ApprovalRequestRecord directly with APPROVED must fail!
    with pytest.raises(ValueError) as exc_info:
        ApprovalRequestRecord(
            approval_request_id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=tx_id,
            authorization_id=uuid.uuid4(),
            authorization_fingerprint="fp_auth_05",
            approval_fingerprint="fp_appr_05",
            amount=Decimal("100.00"),
            currency=SupportedCurrency.INR,
            operation="payment",
            status=ApprovalRequestStatus.APPROVED,  # Illegal initial status!
            risk_score=45.0,
            idempotency_key="idemp_05",
        )

    assert "MUST start as PENDING" in str(exc_info.value)


def test_06_priority_derivation_matrix() -> None:
    """6. Test priority derivation logic for critical, high, medium, and low levels."""
    svc = ApprovalRequestService()

    assert (
        svc._derive_priority(risk_score=85.0, amount=Decimal("100.00"))
        == ApprovalRequestPriority.CRITICAL
    )
    assert (
        svc._derive_priority(risk_score=10.0, amount=Decimal("150000.00"))
        == ApprovalRequestPriority.CRITICAL
    )
    assert (
        svc._derive_priority(risk_score=55.0, amount=Decimal("100.00"))
        == ApprovalRequestPriority.HIGH
    )
    assert (
        svc._derive_priority(risk_score=10.0, amount=Decimal("60000.00"))
        == ApprovalRequestPriority.HIGH
    )
    assert (
        svc._derive_priority(risk_score=35.0, amount=Decimal("100.00"))
        == ApprovalRequestPriority.MEDIUM
    )
    assert (
        svc._derive_priority(risk_score=10.0, amount=Decimal("100.00"))
        == ApprovalRequestPriority.LOW
    )


def test_07_idempotent_duplicate_request_replayed() -> None:
    """7. Test duplicate approval request with same idempotency key returns existing record."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_07"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision_result=decision,
        amount=Decimal("15000.00"),
        currency=SupportedCurrency.INR,
    )

    svc = ApprovalRequestService()
    res1 = svc.create_approval_request(
        decision, policy_req, idempotency_key="idemp_key_07", operation="create_order"
    )
    res2 = svc.create_approval_request(
        decision, policy_req, idempotency_key="idemp_key_07", operation="create_order"
    )

    assert res1.is_existing is False
    assert res2.is_existing is True
    assert res1.request_record.approval_request_id == res2.request_record.approval_request_id


def test_08_idempotency_conflict_raises_409() -> None:
    """8. Test reused idempotency key with modified financial parameters raises 409 Conflict."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_08"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    engine = ApprovalPolicyEngine()
    req1 = engine.evaluate_approval_requirement(
        decision, Decimal("15000.00"), SupportedCurrency.INR
    )
    req2 = engine.evaluate_approval_requirement(
        decision, Decimal("99000.00"), SupportedCurrency.INR
    )

    svc = ApprovalRequestService()
    svc.create_approval_request(decision, req1, idempotency_key="shared_key_08")

    with pytest.raises(ApprovalRequestConflictError) as exc_info:
        svc.create_approval_request(decision, req2, idempotency_key="shared_key_08")

    assert exc_info.value.error_code == "APPROVAL_REQUEST_CONFLICT"


def test_09_multi_tenant_isolation_get_request() -> None:
    """9. Security Test: Cross-tenant request lookup returns None (anti-enumeration)."""
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_req_09"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("1000.00"), SupportedCurrency.INR
    )

    svc = ApprovalRequestService()
    created = svc.create_approval_request(decision, policy_req, idempotency_key="idemp_09")
    req_id = created.request_record.approval_request_id

    # Same tenant -> Found
    assert svc.get_approval_request(tenant_id, req_id) is not None
    # Other tenant -> None (Isolated!)
    assert svc.get_approval_request(other_tenant, req_id) is None


def test_10_record_immutability() -> None:
    """10. Security Test: ApprovalRequestRecord is frozen and immutable."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    record = ApprovalRequestRecord(
        approval_request_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        transaction_id="tx_10",
        authorization_id=uuid.uuid4(),
        authorization_fingerprint="fp_auth_10",
        approval_fingerprint="fp_appr_10",
        amount=Decimal("100.00"),
        currency=SupportedCurrency.INR,
        operation="payment",
        status=ApprovalRequestStatus.PENDING,
        risk_score=45.0,
        idempotency_key="idemp_10",
    )

    with pytest.raises((TypeError, Exception)):
        record.status = ApprovalRequestStatus.APPROVED  # Mutate attempt!


def test_11_static_check_no_direct_razorpay_sdk_imports() -> None:
    """11. Static Check: ApprovalRequestService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.approval_request_service as ars_mod

    source_code = inspect.getsource(ars_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code
