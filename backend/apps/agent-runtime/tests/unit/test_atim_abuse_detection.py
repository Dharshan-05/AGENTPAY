"""Unit tests for ATIM Abuse Detection Service (Phase 18 / Group 9)."""

import uuid

import pytest

from app.application.services.atim_abuse_detection_service import ATIMAbuseDetectionService
from app.domain.governance.policy_models import AbuseAction, AbuseSeverity


@pytest.fixture
def abuse_service():
    return ATIMAbuseDetectionService()


def test_01_abuse_detection_escalation_ladder(abuse_service):
    tenant_id = uuid.uuid4()

    # Step 1: Score 10 -> ALLOW
    r1 = abuse_service.record_abuse_signal(tenant_id, "MALFORMED_INPUT", score_increment=10)
    assert r1.escalation_action == AbuseAction.ALLOW

    # Step 2: Score 35 -> THROTTLE
    r2 = abuse_service.record_abuse_signal(tenant_id, "REPEATED_PROMPT_INJECTION", score_increment=25)
    assert r2.escalation_action == AbuseAction.THROTTLE
    assert r2.severity == AbuseSeverity.MEDIUM

    # Step 3: Score 60 -> REQUIRE_HITL
    r3 = abuse_service.record_abuse_signal(tenant_id, "REPEATED_PROMPT_INJECTION", score_increment=25)
    assert r3.escalation_action == AbuseAction.REQUIRE_HITL
    assert r3.severity == AbuseSeverity.HIGH

    # Step 4: Score 110 -> PERMANENT_SECURITY_BLOCK
    r4 = abuse_service.record_abuse_signal(tenant_id, "CRITICAL_AUTHORIZATION_BYPASS", score_increment=50)
    assert r4.escalation_action == AbuseAction.PERMANENT_SECURITY_BLOCK
    assert r4.severity == AbuseSeverity.CRITICAL
