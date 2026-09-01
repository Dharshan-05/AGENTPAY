"""Unit tests for ATIM Recovery & Transactional Outbox Service (Phase 22 / Group 11)."""

import uuid

import pytest

from app.application.services.atim_recovery_service import ATIMRecoveryService


@pytest.fixture
def recovery_service():
    return ATIMRecoveryService()


def test_01_transactional_outbox_staging_and_dispatch(recovery_service):
    tenant_id = uuid.uuid4()

    event = recovery_service.stage_outbox_event(
        tenant_id=tenant_id,
        event_type="POLICY_ACTIVATED",
        payload={"policy_id": "pol_555", "api_key": "secret_key_12345"},
    )

    assert event.tenant_id == tenant_id
    assert event.processed is False
    assert "api_key" not in event.payload or event.payload["api_key"] in ("[REDACTED]", "[REDACTED_SECRET]")

    dispatched = recovery_service.dispatch_pending_outbox_events(tenant_id)
    assert dispatched == 1


def test_02_disaster_fail_closed_raises_error(recovery_service):
    tenant_id = uuid.uuid4()

    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("PostgreSQL", tenant_id)

    assert "Service Unavailable" in str(exc_info.value)
