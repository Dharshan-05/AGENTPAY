"""Unit and Security Tests for Commerce Engine Integration Subsystem (Phase 183)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.commerce_engine_integration_service import (
    CommerceEngineIntegrationService,
)
from app.domain.exceptions.agent_exceptions import ExecutionValidationError
from app.schemas.inventory import InventoryCheckResult


@pytest.fixture
def service() -> CommerceEngineIntegrationService:
    service = CommerceEngineIntegrationService()
    service.inventory_service.check_inventory = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_unsupported_operation_rejected(
    service: CommerceEngineIntegrationService,
) -> None:
    """1. Test unsupported commerce operation raises ExecutionValidationError."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = MagicMock()

    with pytest.raises(ExecutionValidationError):
        await service.execute_commerce_operation(mock_db, tenant_id, agent_id, "invalid_op", {})


@pytest.mark.asyncio
async def test_02_inventory_check_operation_execution(
    service: CommerceEngineIntegrationService,
) -> None:
    """2. Test inventory_check operation execution wrapper."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    p1_id = uuid.uuid4()

    service.inventory_service.check_inventory.return_value = InventoryCheckResult(  # type: ignore[attr-defined]  # noqa: E501
        product_id=p1_id,
        requested_quantity=Decimal("1.000"),
        available_quantity=Decimal("10.000"),
        is_available=True,
        inventory_status="AVAILABLE",
    )

    mock_db = MagicMock()
    res = await service.execute_commerce_operation(
        mock_db,
        tenant_id,
        agent_id,
        "inventory_check",
        {"product_id": str(p1_id), "quantity": "1.000"},
    )
    assert res["is_available"] is True
    assert res["inventory_status"] == "AVAILABLE"
