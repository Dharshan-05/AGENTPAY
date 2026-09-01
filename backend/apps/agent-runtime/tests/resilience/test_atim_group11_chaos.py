"""Chaos and Resilience tests for ATIM Group 11 (Phase 22)."""

import uuid
import pytest

from app.application.services.atim_recovery_service import ATIMRecoveryService
from app.application.services.atim_idempotency_service import ATIMIdempotencyService
from app.application.services.atim_circuit_breaker import ATIMCircuitBreaker
from app.domain.governance.idempotency_models import IdempotencyState


@pytest.fixture
def recovery_service():
    return ATIMRecoveryService()


@pytest.fixture
def idempotency_service():
    return ATIMIdempotencyService()


def test_01_redis_outage_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("Redis", tenant_id)
    assert "Component 'Redis' is currently unavailable" in str(exc_info.value)


def test_02_postgresql_outage_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("PostgreSQL", tenant_id)
    assert "Component 'PostgreSQL' is currently unavailable" in str(exc_info.value)


def test_03_agentguard_unavailable_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("AGENTGUARD", tenant_id)
    assert "Component 'AGENTGUARD' is currently unavailable" in str(exc_info.value)


def test_04_fraudguard_unavailable_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("FRAUDGUARD", tenant_id)
    assert "Component 'FRAUDGUARD' is currently unavailable" in str(exc_info.value)


def test_05_hitl_unavailable_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("HITL", tenant_id)
    assert "Component 'HITL' is currently unavailable" in str(exc_info.value)


def test_06_audit_service_unavailable_fail_closed(recovery_service):
    tenant_id = uuid.uuid4()
    with pytest.raises(RuntimeError) as exc_info:
        recovery_service.handle_disaster_fail_closed("AuditLockService", tenant_id)
    assert "Component 'AuditLockService' is currently unavailable" in str(exc_info.value)


def test_07_process_crash_reconciliation(recovery_service):
    tenant_id = uuid.uuid4()
    job = recovery_service.reconcile_crashed_workers(tenant_id)
    assert job.status == "COMPLETED"
    assert job.tenant_id == tenant_id
    assert job.reconciled_count >= 0


def test_08_circuit_breaker_transition_resilience():
    cb = ATIMCircuitBreaker(failure_threshold=2)
    provider = "openai"

    cb.record_failure(provider)
    assert cb.get_state(provider).value == "CLOSED"

    cb.record_failure(provider)
    assert cb.get_state(provider).value == "OPEN"
