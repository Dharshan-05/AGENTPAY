"""Unit and Security Tests for Product Personalization Subsystem (Phase 175)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.personalization_service import PersonalizationService
from app.infrastructure.database.models.agent_memory import AgentMemory
from app.infrastructure.database.models.product import Product


@pytest.fixture
def service() -> PersonalizationService:
    return PersonalizationService()


@pytest.mark.asyncio
async def test_01_cold_start_personalization(service: PersonalizationService) -> None:
    """1. Test cold-start handling (no memory or agent_id returns unboosted recommendations)."""
    tenant_id = uuid.uuid4()
    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Laptop",
        sku="LAP-01",
        description="Business laptop",
        price=Decimal("999.00"),
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [p1]

    res = await service.get_personalized_recommendations(mock_db, tenant_id, agent_id=None)
    assert res.personalization_applied is False
    assert len(res.results) == 1
    assert res.results[0].personalization_boost == 0.0


@pytest.mark.asyncio
async def test_02_memory_boosted_personalization(
    service: PersonalizationService,
) -> None:
    """2. Test agent memory preference boost applied to personalized results."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    p1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        merchant_id=uuid.uuid4(),
        name="Wireless Noise Cancelling Headphones",
        sku="HEAD-01",
        description="Bluetooth headphones",
        price=Decimal("199.99"),
        status="active",
    )

    memory_record = AgentMemory(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        namespace="commerce_preferences",
        key="headphones",
        value={"preferred_category": "headphones"},
    )

    mock_db = MagicMock()

    # Mock returns products on first query, memory on second query
    def execute_side_effect(stmt: MagicMock) -> MagicMock:
        mock_scalars = MagicMock()
        stmt_str = str(stmt)
        if "agent_memories" in stmt_str or "namespace" in stmt_str:
            mock_scalars.all.return_value = [memory_record]
        else:
            mock_scalars.all.return_value = [p1]
        mock_res = MagicMock()
        mock_res.scalars.return_value = mock_scalars
        return mock_res

    mock_db.execute.side_effect = execute_side_effect

    res = await service.get_personalized_recommendations(mock_db, tenant_id, agent_id=agent_id)
    assert res.personalization_applied is True
    assert len(res.results) == 1
    assert res.results[0].personalization_boost > 0.0
