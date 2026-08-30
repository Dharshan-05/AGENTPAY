"""Unit, Security & Adversarial Tests for Phase 307 — Approval Expiration Subsystem."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_expiration_service import (
    ApprovalExpirationError,
    ApprovalExpirationService,
)
from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.schemas.approval_expiration import (
    ApprovalExpirationCommand,
    ApprovalExpirationResult,
)
from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.payment import SupportedCurrency
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
        decision_fingerprint="fp_dec_307",
        created_at=datetime.now(UTC),
    )


def test_01_pending_before_deadline_remains_pending() -> None:
    """1. Test PENDING request before TTL deadline remains PENDING."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_01")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService(expiration_ttl_hours=24)
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_01")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)

    # Evaluate 1 hour after creation (deadline is 24 hours)
    now_eval = created.request_record.created_at + timedelta(hours=1)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is False
    assert res.previous_status == ApprovalRequestStatus.PENDING
    assert res.resulting_status == ApprovalRequestStatus.PENDING
    assert res.reason_code == "APPROVAL_NOT_YET_EXPIRED"


def test_02_pending_at_deadline_becomes_expired() -> None:
    """2. Test PENDING request at TTL deadline transitions to EXPIRED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_02")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService(expiration_ttl_hours=24)
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_02")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)

    # Evaluate 24 hours after creation
    now_eval = created.request_record.created_at + timedelta(hours=24)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is True
    assert res.previous_status == ApprovalRequestStatus.PENDING
    assert res.resulting_status == ApprovalRequestStatus.EXPIRED
    assert res.reason_code == "APPROVAL_EXPIRED"

    # Verify status in request_service internal store is EXPIRED
    updated_req = req_svc.get_approval_request(tenant_id, req_id)
    assert updated_req is not None
    assert updated_req.status == ApprovalRequestStatus.EXPIRED


def test_03_pending_after_deadline_becomes_expired() -> None:
    """3. Test PENDING request after TTL deadline transitions to EXPIRED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_03")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService(expiration_ttl_hours=24)
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_03")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)

    now_eval = created.request_record.created_at + timedelta(hours=48)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is True
    assert res.resulting_status == ApprovalRequestStatus.EXPIRED


def test_04_approved_cannot_expire() -> None:
    """4. Security Test: APPROVED request cannot be mutated to EXPIRED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_04")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_04")
    req_id = created.request_record.approval_request_id

    # Mutate status to APPROVED
    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.APPROVED}
    )

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)
    now_eval = created.request_record.created_at + timedelta(hours=48)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is False
    assert res.previous_status == ApprovalRequestStatus.APPROVED
    assert res.resulting_status == ApprovalRequestStatus.APPROVED
    assert res.reason_code == "TERMINAL_STATE_CANNOT_EXPIRE"


def test_05_rejected_cannot_expire() -> None:
    """5. Security Test: REJECTED request cannot be mutated to EXPIRED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_05")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_05")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.REJECTED}
    )

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)
    now_eval = created.request_record.created_at + timedelta(hours=48)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is False
    assert res.resulting_status == ApprovalRequestStatus.REJECTED
    assert res.reason_code == "TERMINAL_STATE_CANNOT_EXPIRE"


def test_06_cancelled_cannot_expire() -> None:
    """6. Security Test: CANCELLED request cannot be mutated to EXPIRED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_06")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_06")
    req_id = created.request_record.approval_request_id

    req_svc._store_by_id[req_id] = req_svc._store_by_id[req_id].model_copy(
        update={"status": ApprovalRequestStatus.CANCELLED}
    )

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)
    now_eval = created.request_record.created_at + timedelta(hours=48)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res.is_expired is False
    assert res.resulting_status == ApprovalRequestStatus.CANCELLED
    assert res.reason_code == "TERMINAL_STATE_CANNOT_EXPIRE"


def test_07_expired_is_idempotent() -> None:
    """7. Test re-expiring an already EXPIRED request is idempotent."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_07")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_07")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)
    now_eval = created.request_record.created_at + timedelta(hours=25)

    res1 = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)
    res2 = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    assert res1.is_expired is True
    assert res1.is_existing is False
    assert res2.is_expired is True
    assert res2.is_existing is True
    assert res2.reason_code == "ALREADY_EXPIRED"


def test_08_request_not_found_raises_error() -> None:
    """8. Security Test: Non-existent approval request raises APPROVAL_REQUEST_NOT_FOUND."""
    tenant_id = uuid.uuid4()
    req_svc = ApprovalRequestService()
    exp_svc = ApprovalExpirationService(request_service=req_svc)

    with pytest.raises(ApprovalExpirationError) as exc_info:
        exp_svc.expire_approval_request(uuid.uuid4(), tenant_id)

    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_09_cross_tenant_expiration_fails() -> None:
    """9. Security Test: Cross-tenant expiration query fails (APPROVAL_REQUEST_NOT_FOUND)."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_a, agent_id, "tx_exp_09")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_09")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc)

    # Tenant B attempts to expire Tenant A's request
    with pytest.raises(ApprovalExpirationError) as exc_info:
        exp_svc.expire_approval_request(req_id, tenant_b)

    assert exc_info.value.error_code == "APPROVAL_REQUEST_NOT_FOUND"


def test_10_batch_expire_eligible_requests() -> None:
    """10. Test expire_eligible_requests batch expires overdue requests for target tenant."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision1 = _make_decision_result(tenant_id, agent_id, "tx_exp_10a")
    decision2 = _make_decision_result(tenant_id, agent_id, "tx_exp_10b")
    engine = ApprovalPolicyEngine()
    req1 = engine.evaluate_approval_requirement(
        decision1, Decimal("10000.00"), SupportedCurrency.INR
    )
    req2 = engine.evaluate_approval_requirement(
        decision2, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created1 = req_svc.create_approval_request(decision1, req1, idempotency_key="idemp_req_10a")
    created2 = req_svc.create_approval_request(decision2, req2, idempotency_key="idemp_req_10b")

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)

    # Evaluate 30 hours later
    now_eval = created1.request_record.created_at + timedelta(hours=30)
    expired_list = exp_svc.expire_eligible_requests(tenant_id=tenant_id, now_utc=now_eval)

    assert len(expired_list) == 2
    req_ids = {r.approval_request_id for r in expired_list}
    assert created1.request_record.approval_request_id in req_ids
    assert created2.request_record.approval_request_id in req_ids


def test_11_secret_redaction_in_expiration_result() -> None:
    """11. Security Test: ApprovalExpirationResult contains zero secrets."""
    assert "key_secret" not in ApprovalExpirationResult.model_fields
    assert "webhook_secret" not in ApprovalExpirationResult.model_fields
    assert "authorization_header" not in ApprovalExpirationResult.model_fields


def test_12_static_check_no_direct_razorpay_sdk_imports() -> None:
    """12. Static Check: ApprovalExpirationService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_13_static_check_no_payment_status_mutation() -> None:
    """13. Static Check: ApprovalExpirationService DOES NOT mutate PaymentStatus."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "transition_status" not in source_code
    assert "PaymentStatusService" not in source_code


def test_14_static_check_no_risk_recalculation() -> None:
    """14. Static Check: ApprovalExpirationService DOES NOT recalculate risk."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "evaluate_approval_requirement" not in source_code
    assert "calculate_composite_score" not in source_code


def test_15_command_extra_forbid() -> None:
    """15. Security Test: ApprovalExpirationCommand rejects extra injected parameters."""
    tenant_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        ApprovalExpirationCommand.model_validate(
            {
                "approval_request_id": str(uuid.uuid4()),
                "tenant_id": str(tenant_id),
                "injected_extra": "unauthorized",
            }
        )


def test_16_timezone_naive_datetime_normalized() -> None:
    """16. Test naive datetime input is normalized to UTC without failing."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_16")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_16")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)

    # Naive datetime 30 hours after creation
    naive_eval = (created.request_record.created_at + timedelta(hours=30)).replace(tzinfo=None)
    res = exp_svc.expire_approval_request(req_id, tenant_id, now_utc=naive_eval)

    assert res.is_expired is True
    assert res.resulting_status == ApprovalRequestStatus.EXPIRED


def test_17_static_check_no_phase_308_audit() -> None:
    """17. Static Check: ApprovalExpirationService DOES NOT implement Phase 308 audit."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "audit_log" not in source_code.lower()
    assert "audit_table" not in source_code.lower()


def test_18_static_check_no_phase_309_continuation() -> None:
    """18. Static Check: ApprovalExpirationService DOES NOT implement Phase 309 continuation."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "create_payment_order" not in source_code
    assert "PaymentService" not in source_code


def test_19_static_check_no_phase_310_human_integration() -> None:
    """19. Static Check: ApprovalExpirationService DOES NOT implement Phase 310 integration."""
    import app.payment.approval.approval_expiration_service as aes_mod

    source_code = inspect.getsource(aes_mod)
    assert "webauthn" not in source_code.lower()
    assert "otp_verify" not in source_code.lower()


def test_20_queue_history_preserves_expired_records() -> None:
    """20. Test queue query infrastructure preserves expired records in history."""
    from app.payment.approval.review_queue_service import ReviewQueueService
    from app.schemas.review_queue import ReviewQueueQuery

    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision = _make_decision_result(tenant_id, agent_id, "tx_exp_20")
    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("10000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    created = req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_req_20")
    req_id = created.request_record.approval_request_id

    exp_svc = ApprovalExpirationService(request_service=req_svc, default_ttl_hours=24)
    now_eval = created.request_record.created_at + timedelta(hours=30)
    exp_svc.expire_approval_request(req_id, tenant_id, now_utc=now_eval)

    # Queue query for status=EXPIRED returns the record
    queue_svc = ReviewQueueService(request_service=req_svc)
    res = queue_svc.query_queue(
        ReviewQueueQuery(tenant_id=tenant_id, status=ApprovalRequestStatus.EXPIRED)
    )

    assert len(res.items) == 1
    assert res.items[0].approval_request_id == req_id
    assert res.items[0].status == ApprovalRequestStatus.EXPIRED
