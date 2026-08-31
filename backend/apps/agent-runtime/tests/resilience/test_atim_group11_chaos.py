"""Chaos and Resilience tests for ATIM Group 11 (Phase 22)."""

import uuid

import pytest

from app.application.services.atim_recovery_service import ATIMRecoveryService


def test_01_redis_outage_fail_closed():
    rec_service = ATIMRecoveryService()
    tenant_id = uuid.uuid4()

    with pytest.raises(RuntimeError) as exc_info:
        rec_service.handle_disaster_fail_closed("Redis", tenant_id)

    assert "Component 'Redis' is currently unavailable" in str(exc_info.value)
