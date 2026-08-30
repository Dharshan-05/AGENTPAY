"""Unit and Security Tests for Transaction Threshold Engine (Phase 191)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.transaction_threshold_service import TransactionThresholdService
from app.schemas.transaction_thresholds import TransactionThresholdEvaluationRequest


@pytest.fixture
def service() -> TransactionThresholdService:
    return TransactionThresholdService()


def test_01_amount_below_all_thresholds_allows(service: TransactionThresholdService) -> None:
    """1. Test amount below all thresholds returns ALLOW."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TransactionThresholdEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("100.00"),
        minimum_amount=Decimal("10.00"),
        maximum_amount=Decimal("1000.00"),
        approval_threshold=Decimal("500.00"),
    )

    res = service.evaluate_threshold(req)
    assert res.decision == "ALLOW"
    assert res.reason_code == "BELOW_THRESHOLD"


def test_02_amount_exceeding_approval_threshold_requires_approval(
    service: TransactionThresholdService,
) -> None:
    """2. Test amount exceeding approval threshold returns REQUIRE_APPROVAL."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TransactionThresholdEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("600.00"),
        approval_threshold=Decimal("500.00"),
        maximum_amount=Decimal("1000.00"),
    )

    res = service.evaluate_threshold(req)
    assert res.decision == "REQUIRE_APPROVAL"
    assert res.reason_code == "APPROVAL_THRESHOLD_EXCEEDED"


def test_03_amount_exceeding_maximum_threshold_denied(
    service: TransactionThresholdService,
) -> None:
    """3. Test amount exceeding maximum threshold returns DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TransactionThresholdEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("1200.00"),
        maximum_amount=Decimal("1000.00"),
    )

    res = service.evaluate_threshold(req)
    assert res.decision == "DENIED"
    assert res.reason_code == "MAXIMUM_THRESHOLD_EXCEEDED"


def test_04_currency_mismatch_fails_closed(service: TransactionThresholdService) -> None:
    """4. Test currency mismatch fails closed with INVALID_CURRENCY."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TransactionThresholdEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("100.00"),
        currency="EUR",
        threshold_currency="USD",
    )

    res = service.evaluate_threshold(req)
    assert res.decision == "DENIED"
    assert res.reason_code == "INVALID_CURRENCY"
