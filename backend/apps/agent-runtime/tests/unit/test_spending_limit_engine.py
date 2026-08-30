"""Unit and Security Tests for Spending Limit Engine (Phase 189)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.spending_limit_service import SpendingLimitService
from app.schemas.spending_limits import SpendingLimitEvaluationRequest


@pytest.fixture
def service() -> SpendingLimitService:
    return SpendingLimitService()


def test_01_spending_limit_within_limit(service: SpendingLimitService) -> None:
    """1. Test spending amount within configured limit passes."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = SpendingLimitEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("150.00"),
        currency="USD",
        configured_limit=Decimal("500.00"),
        limit_currency="USD",
        enforcement_mode="enforce",
    )

    res = service.evaluate_spending_limit(req)
    assert res.decision == "WITHIN_LIMIT"


def test_02_spending_limit_exceeded_denied(service: SpendingLimitService) -> None:
    """2. Test transaction exceeding spending limit is denied."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = SpendingLimitEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("600.00"),
        currency="USD",
        configured_limit=Decimal("500.00"),
        limit_currency="USD",
        enforcement_mode="enforce",
    )

    res = service.evaluate_spending_limit(req)
    assert res.decision == "LIMIT_EXCEEDED"


def test_03_spending_limit_currency_mismatch_fails_closed(
    service: SpendingLimitService,
) -> None:
    """3. Test currency mismatch fails closed with INVALID_CURRENCY."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = SpendingLimitEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        amount=Decimal("100.00"),
        currency="EUR",
        configured_limit=Decimal("500.00"),
        limit_currency="USD",
        enforcement_mode="enforce",
    )

    res = service.evaluate_spending_limit(req)
    assert res.decision == "INVALID_CURRENCY"
