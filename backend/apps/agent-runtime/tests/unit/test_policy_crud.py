"""Unit and Security Tests for Policy CRUD Subsystem (Phase 186)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.application.services.policy_service import PolicyService
from app.domain.exceptions.policy_exceptions import PolicyNotFoundError
from app.infrastructure.database.models.security_policy import SecurityPolicy
from app.schemas.policies import PolicyCreateRequest


@pytest.fixture
def service() -> PolicyService:
    return PolicyService()


@pytest.mark.asyncio
async def test_01_create_policy_success(service: PolicyService) -> None:
    """1. Test successful policy creation."""
    tenant_id = uuid.uuid4()
    req = PolicyCreateRequest(
        name="Spending Cap",
        description="Limit max transaction amount",
        policy_type="spending",
        priority=100,
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    res = await service.create_policy(mock_db, tenant_id, req)
    assert res.name == "Spending Cap"
    assert res.slug == "spending-cap"
    assert res.status == "draft"
    assert res.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_02_get_policy_not_found_raises_404(service: PolicyService) -> None:
    """2. Test policy lookup for non-existent policy raises PolicyNotFoundError."""
    tenant_id = uuid.uuid4()
    policy_id = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    with pytest.raises(PolicyNotFoundError):
        await service.get_policy(mock_db, tenant_id, policy_id)


@pytest.mark.asyncio
async def test_03_activate_deactivate_archive_policy_lifecycle(
    service: PolicyService,
) -> None:
    """3. Test policy status lifecycle transitions."""
    tenant_id = uuid.uuid4()
    policy_id = uuid.uuid4()

    policy = SecurityPolicy(
        id=policy_id,
        tenant_id=tenant_id,
        name="Test Policy",
        slug="test-policy",
        status="draft",
        policy_type="spending",
        priority=100,
        enforcement_mode="enforce",
        version=1,
        configuration={},
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = policy

    act_res = await service.activate_policy(mock_db, tenant_id, policy_id)
    assert act_res.status == "active"
    assert act_res.version == 2

    deact_res = await service.deactivate_policy(mock_db, tenant_id, policy_id)
    assert deact_res.status == "inactive"

    arch_res = await service.archive_policy(mock_db, tenant_id, policy_id)
    assert arch_res.status == "archived"
