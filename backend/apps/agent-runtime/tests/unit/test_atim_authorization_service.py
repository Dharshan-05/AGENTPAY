"""Unit tests for ATIM Authorization Service & Tenant Isolation Boundary (Phase 19 / Group 10)."""

import uuid

import pytest

from app.application.services.atim_authorization_service import ATIMAuthorizationService
from app.domain.governance.compliance_models import ATIMSecurityContext, SecurityPermission


@pytest.fixture
def auth_service():
    return ATIMAuthorizationService()


def test_01_authorize_permission_granted(auth_service):
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    ctx = ATIMSecurityContext(
        user_id=user_id,
        tenant_id=tenant_id,
        permissions=[SecurityPermission.ATIM_POLICY_READ, SecurityPermission.ATIM_POLICY_CREATE],
    )

    # Should not raise exception
    auth_service.authorize_permission(ctx, SecurityPermission.ATIM_POLICY_READ)


def test_02_authorize_permission_missing_raises_error(auth_service):
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    ctx = ATIMSecurityContext(
        user_id=user_id,
        tenant_id=tenant_id,
        permissions=[SecurityPermission.ATIM_POLICY_READ],
    )

    # User lacks ATIM_POLICY_APPROVE
    with pytest.raises(PermissionError) as exc_info:
        auth_service.authorize_permission(ctx, SecurityPermission.ATIM_POLICY_APPROVE)

    assert "Missing required permission" in str(exc_info.value)


def test_03_verify_tenant_boundary_same_tenant(auth_service):
    tenant_id = uuid.uuid4()
    ctx = ATIMSecurityContext(user_id=uuid.uuid4(), tenant_id=tenant_id)

    # Same tenant -> allowed
    auth_service.verify_tenant_boundary(ctx, tenant_id)


def test_04_verify_tenant_boundary_cross_tenant_raises_error(auth_service):
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    ctx = ATIMSecurityContext(user_id=uuid.uuid4(), tenant_id=tenant_a)

    # Accessing tenant B -> forbidden
    with pytest.raises(PermissionError) as exc_info:
        auth_service.verify_tenant_boundary(ctx, tenant_b)

    assert "Cross-tenant operation is forbidden" in str(exc_info.value)
