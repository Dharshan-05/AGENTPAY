"""Unit and Security Tests for Time-Based Policy Engine (Phase 194)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.application.services.time_based_policy_service import TimeBasedPolicyService
from app.schemas.time_based_policies import TimeBasedPolicyEvaluationRequest


@pytest.fixture
def service() -> TimeBasedPolicyService:
    return TimeBasedPolicyService()


def test_01_always_active_policy_passes(service: TimeBasedPolicyService) -> None:
    """1. Test unconstrained time policy returns is_eligible = True."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TimeBasedPolicyEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = service.evaluate_time_eligibility(req)
    assert res.is_eligible is True
    assert res.window_type == "ALWAYS_ACTIVE"
    assert res.reason_code == "TIME_POLICY_ACTIVE"


def test_02_outside_date_range_expired(service: TimeBasedPolicyService) -> None:
    """2. Test evaluation timestamp past ends_at returns is_eligible = False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TimeBasedPolicyEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        evaluation_time=datetime(2026, 9, 1, 12, 0, 0, tzinfo=UTC),
        ends_at=datetime(2026, 8, 31, 23, 59, 59, tzinfo=UTC),
    )

    res = service.evaluate_time_eligibility(req)
    assert res.is_eligible is False
    assert res.reason_code == "POLICY_EXPIRED"


def test_03_time_window_midnight_crossing(service: TimeBasedPolicyService) -> None:
    """3. Test overnight time window crossing midnight (e.g., 22:00 -> 06:00)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    # 23:30 is within 22:00 -> 06:00
    req_inside = TimeBasedPolicyEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        evaluation_time=datetime(2026, 8, 26, 23, 30, 0, tzinfo=UTC),
        time_window_start="22:00",
        time_window_end="06:00",
    )
    res_inside = service.evaluate_time_eligibility(req_inside)
    assert res_inside.is_eligible is True

    # 12:00 is outside 22:00 -> 06:00
    req_outside = TimeBasedPolicyEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        evaluation_time=datetime(2026, 8, 26, 12, 0, 0, tzinfo=UTC),
        time_window_start="22:00",
        time_window_end="06:00",
    )
    res_outside = service.evaluate_time_eligibility(req_outside)
    assert res_outside.is_eligible is False
    assert res_outside.reason_code == "OUTSIDE_TIME_WINDOW"


def test_04_invalid_timezone_fails_closed(service: TimeBasedPolicyService) -> None:
    """4. Test invalid timezone name fails closed."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TimeBasedPolicyEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        timezone="Invalid/NonExistent_TZ",
    )

    res = service.evaluate_time_eligibility(req)
    assert res.is_eligible is False
    assert res.reason_code == "INVALID_TIMEZONE"
