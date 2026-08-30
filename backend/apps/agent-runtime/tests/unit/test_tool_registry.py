"""Unit and Security Tests for Tool Registry Subsystem (Phase 157)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.tool_registry_service import ToolRegistryService
from app.domain.exceptions.agent_exceptions import ToolAlreadyExistsError
from app.infrastructure.database.models.tool_definition import ToolDefinition
from app.schemas.tool_registry import (
    ToolRegisterRequest,
    ToolRiskClassification,
    ToolStatus,
)


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def service() -> ToolRegistryService:
    service = ToolRegistryService()
    service.audit_service.record_audit_event = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_register_tool_success(mock_db: MagicMock, service: ToolRegistryService) -> None:
    """1. Test successful tool registration in central registry."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    req = ToolRegisterRequest(
        tool_id="currency_converter",
        name="Currency Converter",
        version="1.0.0",
        description="Converts amounts between currencies",
        category="finance",
        risk_classification=ToolRiskClassification.LOW,
        input_schema={
            "type": "object",
            "required": ["amount", "from_currency", "to_currency"],
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
        },
    )

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    res = await service.register_tool(mock_db, tenant_id, user_id, req)
    assert res.tool_id == "currency_converter"
    assert res.status == ToolStatus.REGISTERED
    assert res.version == "1.0.0"


@pytest.mark.asyncio
async def test_02_register_duplicate_tool_rejected(
    mock_db: MagicMock, service: ToolRegistryService
) -> None:
    """2. Test duplicate tool registration with same name and version is rejected."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    req = ToolRegisterRequest(
        tool_id="currency_converter",
        name="Currency Converter",
        version="1.0.0",
        description="Converts amounts between currencies",
    )

    mock_existing = MagicMock(spec=ToolDefinition)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_existing

    with pytest.raises(ToolAlreadyExistsError):
        await service.register_tool(mock_db, tenant_id, user_id, req)


@pytest.mark.asyncio
async def test_03_enable_and_disable_tool(mock_db: MagicMock, service: ToolRegistryService) -> None:
    """3. Test enabling and disabling registered tool."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    tool_id = "payment_processor"

    mock_tool = MagicMock(spec=ToolDefinition)
    mock_tool.id = uuid.uuid4()
    mock_tool.tenant_id = tenant_id
    mock_tool.tool_id = tool_id
    mock_tool.name = "Payment Processor"
    mock_tool.version = "1.0.0"
    mock_tool.description = "Processes payments"
    mock_tool.category = "finance"
    mock_tool.owner = "admin"
    mock_tool.status = "REGISTERED"
    mock_tool.environment = "production"
    mock_tool.risk_classification = "HIGH"
    mock_tool.input_schema = {}
    mock_tool.output_schema = {}
    mock_tool.capabilities = []
    mock_tool.tool_metadata = {}
    mock_tool.created_at = datetime.now(UTC)
    mock_tool.updated_at = datetime.now(UTC)

    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_tool

    # Enable
    await service.enable_tool(mock_db, tenant_id, user_id, tool_id)
    assert mock_tool.status == "ENABLED"

    # Disable
    await service.disable_tool(mock_db, tenant_id, user_id, tool_id)
    assert mock_tool.status == "DISABLED"
