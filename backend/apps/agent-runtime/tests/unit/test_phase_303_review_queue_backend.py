"""Unit, Security & Adversarial Tests for Phase 303 — Review Queue Backend."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.payment.approval.approval_policy_engine import ApprovalPolicyEngine
from app.payment.approval.approval_request_service import ApprovalRequestService
from app.payment.approval.review_queue_service import ReviewQueueService
from app.schemas.approval_request import (
    ApprovalRequestPriority,
    ApprovalRequestStatus,
)
from app.schemas.payment import SupportedCurrency
from app.schemas.review_queue import (
    ReviewQueueItem,
    ReviewQueueQuery,
    ReviewQueueResult,
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
        decision_fingerprint="fp_dec_303",
        created_at=datetime.now(UTC),
    )


def test_01_valid_queue_query() -> None:
    """1. Test valid review queue query returns pending items for target tenant."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    tx_id = "tx_q_01"
    decision = _make_decision_result(tenant_id, agent_id, tx_id)

    engine = ApprovalPolicyEngine()
    policy_req = engine.evaluate_approval_requirement(
        decision, Decimal("15000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    req_svc.create_approval_request(decision, policy_req, idempotency_key="idemp_q_01")

    queue_svc = ReviewQueueService(request_service=req_svc)
    query = ReviewQueueQuery(tenant_id=tenant_id, status=ApprovalRequestStatus.PENDING)

    res = queue_svc.query_queue(query)
    assert isinstance(res, ReviewQueueResult)
    assert len(res.items) == 1
    assert res.total_count == 1
    assert res.items[0].transaction_id == tx_id
    assert res.items[0].tenant_id == tenant_id


def test_02_tenant_isolation_in_queue_query() -> None:
    """2. Security Test: Tenant A cannot see Tenant B review queue items."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    decision_a = _make_decision_result(tenant_a, agent_id, "tx_tenant_a")
    decision_b = _make_decision_result(tenant_b, agent_id, "tx_tenant_b")

    engine = ApprovalPolicyEngine()
    req_a = engine.evaluate_approval_requirement(
        decision_a, Decimal("10000.00"), SupportedCurrency.INR
    )
    req_b = engine.evaluate_approval_requirement(
        decision_b, Decimal("20000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    req_svc.create_approval_request(decision_a, req_a, idempotency_key="idemp_tenant_a")
    req_svc.create_approval_request(decision_b, req_b, idempotency_key="idemp_tenant_b")

    queue_svc = ReviewQueueService(request_service=req_svc)

    res_a = queue_svc.query_queue(ReviewQueueQuery(tenant_id=tenant_a))
    res_b = queue_svc.query_queue(ReviewQueueQuery(tenant_id=tenant_b))

    assert len(res_a.items) == 1
    assert res_a.items[0].transaction_id == "tx_tenant_a"

    assert len(res_b.items) == 1
    assert res_b.items[0].transaction_id == "tx_tenant_b"


def test_03_controlled_operation_filtering() -> None:
    """3. Test filtering review queue by operation (e.g. refund vs create_order)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    d1 = _make_decision_result(tenant_id, agent_id, "tx_op_1")
    d2 = _make_decision_result(tenant_id, agent_id, "tx_op_2")

    engine = ApprovalPolicyEngine()
    req1 = engine.evaluate_approval_requirement(
        d1, Decimal("1000.00"), SupportedCurrency.INR, operation="create_order"
    )
    req2 = engine.evaluate_approval_requirement(
        d2, Decimal("2000.00"), SupportedCurrency.INR, operation="refund"
    )

    req_svc = ApprovalRequestService()
    req_svc.create_approval_request(
        d1, req1, idempotency_key="idemp_op_1", operation="create_order"
    )
    req_svc.create_approval_request(d2, req2, idempotency_key="idemp_op_2", operation="refund")

    queue_svc = ReviewQueueService(request_service=req_svc)

    res_refunds = queue_svc.query_queue(ReviewQueueQuery(tenant_id=tenant_id, operation="refund"))
    assert len(res_refunds.items) == 1
    assert res_refunds.items[0].operation == "refund"


def test_04_priority_filtering() -> None:
    """4. Test minimum priority threshold filtering (min_priority=HIGH)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    # Low risk score -> LOW priority
    d_low = _make_decision_result(tenant_id, agent_id, "tx_low", score=10.0)
    # High risk score -> CRITICAL priority
    d_crit = _make_decision_result(tenant_id, agent_id, "tx_crit", score=85.0)

    engine = ApprovalPolicyEngine()
    req_low = engine.evaluate_approval_requirement(d_low, Decimal("100.00"), SupportedCurrency.INR)
    req_crit = engine.evaluate_approval_requirement(
        d_crit, Decimal("150000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    req_svc.create_approval_request(d_low, req_low, idempotency_key="idemp_prio_low")
    req_svc.create_approval_request(d_crit, req_crit, idempotency_key="idemp_prio_crit")

    queue_svc = ReviewQueueService(request_service=req_svc)

    res_crit = queue_svc.query_queue(
        ReviewQueueQuery(tenant_id=tenant_id, min_priority=ApprovalRequestPriority.CRITICAL)
    )
    assert len(res_crit.items) == 1
    assert res_crit.items[0].priority == ApprovalRequestPriority.CRITICAL


def test_05_deterministic_priority_ordering() -> None:
    """5. Test queue items are deterministically sorted by priority DESC."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    d_low = _make_decision_result(tenant_id, agent_id, "tx_low", score=10.0)
    d_crit = _make_decision_result(tenant_id, agent_id, "tx_crit", score=90.0)

    engine = ApprovalPolicyEngine()
    req_low = engine.evaluate_approval_requirement(d_low, Decimal("100.00"), SupportedCurrency.INR)
    req_crit = engine.evaluate_approval_requirement(
        d_crit, Decimal("200000.00"), SupportedCurrency.INR
    )

    req_svc = ApprovalRequestService()
    # Insert LOW priority first
    req_svc.create_approval_request(d_low, req_low, idempotency_key="idemp_order_1")
    # Insert CRITICAL priority second
    req_svc.create_approval_request(d_crit, req_crit, idempotency_key="idemp_order_2")

    queue_svc = ReviewQueueService(request_service=req_svc)
    res = queue_svc.query_queue(ReviewQueueQuery(tenant_id=tenant_id))

    # CRITICAL must appear BEFORE LOW despite created later!
    assert len(res.items) == 2
    assert res.items[0].priority == ApprovalRequestPriority.CRITICAL
    assert res.items[1].priority == ApprovalRequestPriority.LOW


def test_06_bounded_page_size_validation() -> None:
    """6. Security Test: Page size > 100 raises ValidationError to prevent memory exhaustion."""
    tenant_id = uuid.uuid4()

    with pytest.raises((ValueError, ValidationError)) as exc_info:
        ReviewQueueQuery.model_validate({"tenant_id": str(tenant_id), "page_size": 99999})

    assert "100" in str(exc_info.value)


def test_07_keyset_pagination() -> None:
    """7. Test keyset pagination divides items correctly and calculates next_cursor."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    req_svc = ApprovalRequestService()
    engine = ApprovalPolicyEngine()

    for i in range(3):
        tx_id = f"tx_page_{i}"
        d = _make_decision_result(tenant_id, agent_id, tx_id, score=45.0)
        p_req = engine.evaluate_approval_requirement(d, Decimal("50000.00"), SupportedCurrency.INR)
        req_svc.create_approval_request(d, p_req, idempotency_key=f"idemp_pg_{i}")

    queue_svc = ReviewQueueService(request_service=req_svc)

    # Page 1 (page_size = 2)
    q1 = ReviewQueueQuery(tenant_id=tenant_id, page_size=2)
    res1 = queue_svc.query_queue(q1)

    assert len(res1.items) == 2
    assert res1.total_count == 3
    assert res1.next_cursor_created_at is not None
    assert res1.next_cursor_id is not None

    # Page 2 using cursor
    q2 = ReviewQueueQuery(
        tenant_id=tenant_id,
        page_size=2,
        cursor_created_at=res1.next_cursor_created_at,
        cursor_id=res1.next_cursor_id,
    )
    res2 = queue_svc.query_queue(q2)

    assert len(res2.items) == 1
    assert res2.items[0].approval_request_id != res1.items[0].approval_request_id


def test_08_secret_redaction_in_queue_item() -> None:
    """8. Security Test: ReviewQueueItem model_fields contain 0 secret fields."""
    assert "key_secret" not in ReviewQueueItem.model_fields
    assert "webhook_secret" not in ReviewQueueItem.model_fields
    assert "authorization_header" not in ReviewQueueItem.model_fields


def test_09_static_check_no_direct_razorpay_sdk_imports() -> None:
    """9. Static Check: ReviewQueueService DOES NOT import razorpay SDK directly."""
    import app.payment.approval.review_queue_service as rqs_mod

    source_code = inspect.getsource(rqs_mod)
    assert "import razorpay" not in source_code
    assert "from razorpay" not in source_code


def test_10_static_check_no_approval_execution_routines() -> None:
    """10. Static Check: ReviewQueueService DOES NOT contain execution routines."""
    import app.payment.approval.review_queue_service as rqs_mod

    source_code = inspect.getsource(rqs_mod)
    assert "execute_payment" not in source_code
    assert "approve_payment" not in source_code
