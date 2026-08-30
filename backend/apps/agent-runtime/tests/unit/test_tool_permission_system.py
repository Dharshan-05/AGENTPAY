"""Unit and Security Tests for Tool Permission System (Phase 158)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.tool_authorization_service import ToolAuthorizationService
from app.domain.authorization.permissions_registry import TOOLS_EXECUTE
from app.schemas.tool_authorization import (
    ToolAuthorizationContext,
    ToolAuthorizationDecisionEnum,
)
from app.schemas.tool_registry import ToolRiskClassification


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def auth_service() -> ToolAuthorizationService:
    service = ToolAuthorizationService()
    service.rbac_service.resolve_agent_permissions = AsyncMock()  # type: ignore[method-assign]
    service.approval_service.evaluate_approval_policy = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_evaluate_authorization_allow_low_risk(
    mock_db: MagicMock, auth_service: ToolAuthorizationService
) -> None:
    """1. Test low-risk tool execution with TOOLS_EXECUTE returns ALLOW."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    auth_service.rbac_service.resolve_agent_permissions.return_value = frozenset([TOOLS_EXECUTE])  # type: ignore[attr-defined]  # noqa: E501
    mock_policy = MagicMock()
    mock_policy.requires_approval = False
    mock_policy.matched_policy_name = None
    auth_service.approval_service.evaluate_approval_policy.return_value = mock_policy  # type: ignore[attr-defined]  # noqa: E501

    ctx = ToolAuthorizationContext(
        tenant_id=tenant_id,
        agent_id=agent_id,
        tool_id="weather_check",
        risk_classification=ToolRiskClassification.LOW,
    )

    res = await auth_service.evaluate_authorization(mock_db, ctx)
    assert res.decision == ToolAuthorizationDecisionEnum.ALLOW
    assert res.requires_approval is False


@pytest.mark.asyncio
async def test_02_evaluate_authorization_deny_missing_permission(
    mock_db: MagicMock, auth_service: ToolAuthorizationService
) -> None:
    """2. Test tool execution without TOOLS_EXECUTE permission returns DENY."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    auth_service.rbac_service.resolve_agent_permissions.return_value = frozenset(["tools:read"])  # type: ignore[attr-defined]  # noqa: E501

    ctx = ToolAuthorizationContext(
        tenant_id=tenant_id,
        agent_id=agent_id,
        tool_id="data_exporter",
        risk_classification=ToolRiskClassification.LOW,
    )

    res = await auth_service.evaluate_authorization(mock_db, ctx)
    assert res.decision == ToolAuthorizationDecisionEnum.DENY
    assert "lacks mandatory" in res.reason


@pytest.mark.asyncio
async def test_03_evaluate_authorization_require_approval_high_risk(
    mock_db: MagicMock, auth_service: ToolAuthorizationService
) -> None:
    """3. Test high-risk or large financial operation returns REQUIRE_APPROVAL."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    auth_service.rbac_service.resolve_agent_permissions.return_value = frozenset([TOOLS_EXECUTE])  # type: ignore[attr-defined]  # noqa: E501
    mock_policy = MagicMock()
    mock_policy.requires_approval = True
    mock_policy.matched_policy_name = "High Risk Multi-Approval Policy"
    auth_service.approval_service.evaluate_approval_policy.return_value = mock_policy  # type: ignore[attr-defined]  # noqa: E501

    ctx = ToolAuthorizationContext(
        tenant_id=tenant_id,
        agent_id=agent_id,
        tool_id="payment_initiation",
        risk_classification=ToolRiskClassification.HIGH,
        amount=150.00,
    )

    res = await auth_service.evaluate_authorization(mock_db, ctx)
    assert res.decision == ToolAuthorizationDecisionEnum.REQUIRE_APPROVAL
    assert res.requires_approval is True
    assert res.approval_policy_name == "High Risk Multi-Approval Policy"
