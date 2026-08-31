"""Unit tests for ATIM Quota Service (Phase 18 / Group 9)."""

from decimal import Decimal
import uuid

import pytest

from app.application.services.atim_quota_service import ATIMQuotaService


@pytest.fixture
def quota_service():
    return ATIMQuotaService()


def test_01_quota_consumption_clean_flow(quota_service):
    tenant_id = uuid.uuid4()
    is_allowed, reason, quota = quota_service.check_and_consume_quota(
        tenant_id=tenant_id,
        tokens_requested=500,
        cost_requested_usd=Decimal("0.005000"),
    )

    assert is_allowed is True
    assert quota.current_daily_requests == 1
    assert quota.current_daily_tokens == 500
    assert quota.current_daily_cost_usd == Decimal("0.005000")


def test_02_quota_violation_requests_exceeded(quota_service):
    tenant_id = uuid.uuid4()
    quota = quota_service.get_or_create_quota(tenant_id)
    quota.max_requests_per_day = 1
    quota.current_daily_requests = 1

    is_allowed, reason, _ = quota_service.check_and_consume_quota(
        tenant_id=tenant_id,
        tokens_requested=10,
        cost_requested_usd=Decimal("0.000100"),
    )

    assert is_allowed is False
    assert "Daily request quota exceeded" in reason
