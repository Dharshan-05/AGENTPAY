"""Unit tests for ATIM Sliding-Window Rate Limiter Engine (Phase 18 / Group 9)."""

import uuid

import pytest

from app.application.services.atim_rate_limiter import ATIMRateLimiter


@pytest.fixture
def rate_limiter():
    return ATIMRateLimiter(default_limit=2, window_seconds=60)


def test_01_rate_limiter_allows_under_limit(rate_limiter):
    tenant_id = uuid.uuid4()

    res1 = rate_limiter.check_rate_limit(tenant_id)
    assert res1.allowed is True
    assert res1.remaining == 1

    res2 = rate_limiter.check_rate_limit(tenant_id)
    assert res2.allowed is True
    assert res2.remaining == 0


def test_02_rate_limiter_blocks_above_limit(rate_limiter):
    tenant_id = uuid.uuid4()

    rate_limiter.check_rate_limit(tenant_id)
    rate_limiter.check_rate_limit(tenant_id)

    # 3rd request breaches limit of 2
    res3 = rate_limiter.check_rate_limit(tenant_id)
    assert res3.allowed is False
    assert res3.remaining == 0
    assert res3.retry_after_seconds > 0
