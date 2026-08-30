"""Unit and Security Tests for Behaviour Deviation Engine (Phase 202)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.behaviour_deviation_service import BehaviourDeviationService
from app.schemas.behaviour_baseline import AmountStatistics, BehaviourBaseline
from app.schemas.behaviour_deviation import BehaviourDeviationRequest


@pytest.fixture
def service() -> BehaviourDeviationService:
    return BehaviourDeviationService()


def test_01_normal_action_within_baseline(
    service: BehaviourDeviationService,
) -> None:
    """1. Test action fitting historical baseline returns has_deviation = False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    baseline = BehaviourBaseline(
        agent_id=agent_id,
        tenant_id=tenant_id,
        baseline_available=True,
        state="ESTABLISHED",
        observation_count=10,
        successful_count=10,
        failed_count=0,
        amount_stats=AmountStatistics(
            total_amount=Decimal("1000.00"),
            average_amount=Decimal("100.00"),
            min_amount=Decimal("50.00"),
            max_amount=Decimal("200.00"),
        ),
        frequent_merchants=[str(merchant_id).lower()],
        frequent_categories=["electronics"],
        frequent_currencies=["USD"],
    )

    req = BehaviourDeviationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("120.00"),
        currency="USD",
        merchant_id=merchant_id,
        category="electronics",
        baseline=baseline,
    )

    res = service.evaluate_deviation(req)
    assert res.has_deviation is False
    assert res.severity == "NORMAL"


def test_02_critical_amount_deviation_detected(
    service: BehaviourDeviationService,
) -> None:
    """2. Test transaction exceeding 2x max baseline returns CRITICAL amount deviation."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    baseline = BehaviourBaseline(
        agent_id=agent_id,
        tenant_id=tenant_id,
        baseline_available=True,
        state="ESTABLISHED",
        observation_count=10,
        successful_count=10,
        failed_count=0,
        amount_stats=AmountStatistics(
            total_amount=Decimal("1000.00"),
            average_amount=Decimal("100.00"),
            min_amount=Decimal("50.00"),
            max_amount=Decimal("200.00"),
        ),
    )

    req = BehaviourDeviationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("500.00"),
        baseline=baseline,
    )

    res = service.evaluate_deviation(req)
    assert res.has_deviation is True
    assert res.severity == "CRITICAL"
    assert "AMOUNT_DEVIATION_CRITICAL" in res.reason_codes
