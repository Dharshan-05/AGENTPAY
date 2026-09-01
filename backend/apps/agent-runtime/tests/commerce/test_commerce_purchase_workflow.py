"""Unit Tests for Purchase Workflow State Machine & Price Revalidation (Buildathon Track 01)."""

import uuid
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.commerce.schemas import PurchaseWorkflowRequest
from app.commerce.services.purchase_workflow_service import PurchaseWorkflowService


@pytest.mark.asyncio
async def test_purchase_workflow_price_revalidation_mismatch():
    """Verify price revalidation halts workflow if price changes (₹47,990 -> ₹51,490)."""
    service = PurchaseWorkflowService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    # User requested purchase at ₹44,000, but revalidated price is ₹47,990
    req = PurchaseWorkflowRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        product_id="prod_lenovo_ideapad_slim3",
        product_name="Lenovo IdeaPad Slim 3",
        price=Decimal("44000.00"),
        currency="INR",
        seller_id="seller_lenovo_official_india",
    )

    res = await service.initiate_purchase_workflow(db=mock_db, request=req)

    assert res.price_changed is True
    assert "PRICE_CHANGED" in (res.price_change_message or "")
    assert res.workflow_status == "PRICE_MISMATCH"
    assert res.final_execution_decision == "DENY"


@pytest.mark.asyncio
async def test_purchase_workflow_clean_initiation():
    """Verify clean price match initiates HITL approval request."""
    service = PurchaseWorkflowService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = PurchaseWorkflowRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        product_id="prod_lenovo_ideapad_slim3",
        product_name="Lenovo IdeaPad Slim 3",
        price=Decimal("47990.00"),
        currency="INR",
        seller_id="seller_lenovo_official_india",
    )

    res = await service.initiate_purchase_workflow(db=mock_db, request=req)

    assert res.price_changed is False
    assert res.workflow_status == "PENDING_HITL"
    assert res.hitl_required is True
    assert res.hitl_approval_id is not None
    assert res.final_execution_decision == "REVIEW"
