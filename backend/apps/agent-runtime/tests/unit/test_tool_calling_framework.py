"""Unit and Security Tests for Tool Calling Framework (Phase 156)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.tool_execution_service import ToolExecutionService
from app.domain.exceptions.agent_exceptions import ToolDisabledError, ToolValidationError
from app.schemas.tool_calling import ToolCallRequest, ToolExecutionState
from app.schemas.tool_registry import ToolResponse, ToolRiskClassification, ToolStatus


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    return db


@pytest.fixture
def service() -> ToolExecutionService:
    service = ToolExecutionService()
    service.audit_service.record_audit_event = AsyncMock()  # type: ignore[method-assign]
    service.tool_audit_service.record_tool_execution_audit = AsyncMock()  # type: ignore[method-assign]  # noqa: E501
    service.registry_service.get_tool = AsyncMock()  # type: ignore[method-assign]

    mock_auth_res = MagicMock()
    mock_auth_res.decision.value = "ALLOW"
    from app.schemas.tool_authorization import ToolAuthorizationDecisionEnum

    mock_auth_res.decision = ToolAuthorizationDecisionEnum.ALLOW
    service.auth_service.evaluate_authorization = AsyncMock(return_value=mock_auth_res)  # type: ignore[method-assign]  # noqa: E501
    return service


@pytest.mark.asyncio
async def test_01_execute_tool_success(mock_db: MagicMock, service: ToolExecutionService) -> None:
    """1. Test successful execution of a registered tool."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_tool = ToolResponse(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tool_id="weather_query",
        name="Weather Query",
        version="1.0.0",
        description="Fetch weather",
        category="utility",
        owner=None,
        status=ToolStatus.ENABLED,
        environment="production",
        risk_classification=ToolRiskClassification.LOW,
        input_schema={
            "type": "object",
            "required": ["city"],
            "properties": {"city": {"type": "string"}},
        },
        output_schema={},
        capabilities=["weather"],
        metadata={},
        created_at=pytest.importorskip("datetime").datetime.now(),
        updated_at=pytest.importorskip("datetime").datetime.now(),
    )

    service.registry_service.get_tool = AsyncMock(return_value=mock_tool)  # type: ignore[method-assign]  # noqa: E501

    req = ToolCallRequest(
        tool_id="weather_query",
        arguments={"city": "San Francisco"},
    )

    res = await service.execute_tool(mock_db, tenant_id, agent_id, req, user_id=user_id)
    assert res.state == ToolExecutionState.SUCCEEDED
    assert res.result is not None
    assert res.result.status == "success"


@pytest.mark.asyncio
async def test_02_disabled_tool_execution_rejected(
    mock_db: MagicMock, service: ToolExecutionService
) -> None:
    """2. Test execution request for a disabled tool is rejected."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_tool = ToolResponse(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tool_id="disabled_tool",
        name="Disabled Tool",
        version="1.0.0",
        description="Disabled tool",
        category="utility",
        owner=None,
        status=ToolStatus.DISABLED,
        environment="production",
        risk_classification=ToolRiskClassification.LOW,
        input_schema={},
        output_schema={},
        capabilities=[],
        metadata={},
        created_at=pytest.importorskip("datetime").datetime.now(),
        updated_at=pytest.importorskip("datetime").datetime.now(),
    )

    service.registry_service.get_tool = AsyncMock(return_value=mock_tool)  # type: ignore[method-assign]  # noqa: E501

    req = ToolCallRequest(tool_id="disabled_tool", arguments={})

    with pytest.raises(ToolDisabledError):
        await service.execute_tool(mock_db, tenant_id, agent_id, req)


@pytest.mark.asyncio
async def test_03_malformed_argument_validation_failed(
    mock_db: MagicMock, service: ToolExecutionService
) -> None:
    """3. Test malformed or missing argument validation failures."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_tool = ToolResponse(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tool_id="calculator",
        name="Calculator",
        version="1.0.0",
        description="Calculator",
        category="math",
        owner=None,
        status=ToolStatus.ENABLED,
        environment="production",
        risk_classification=ToolRiskClassification.LOW,
        input_schema={
            "type": "object",
            "required": ["number"],
            "properties": {"number": {"type": "number"}},
        },
        output_schema={},
        capabilities=[],
        metadata={},
        created_at=pytest.importorskip("datetime").datetime.now(),
        updated_at=pytest.importorskip("datetime").datetime.now(),
    )

    service.registry_service.get_tool = AsyncMock(return_value=mock_tool)  # type: ignore[method-assign]  # noqa: E501

    # Missing required 'number' argument
    req = ToolCallRequest(tool_id="calculator", arguments={})

    with pytest.raises(ToolValidationError, match="Missing required tool argument"):
        await service.execute_tool(mock_db, tenant_id, agent_id, req)
