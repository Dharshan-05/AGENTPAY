"""Unit Tests for Razorpay Test-Mode Integration & Idempotency Boundary (Buildathon Track 01)."""

import uuid
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.commerce.schemas import PaymentConfirmationRequest
from app.commerce.services.commerce_payment_orchestrator import CommercePaymentOrchestrator


@pytest.mark.asyncio
async def test_razorpay_test_mode_payment_execution_and_idempotency():
    """Verify Razorpay test order creation and idempotency caching to prevent double-charging."""
    orchestrator = CommercePaymentOrchestrator()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    workflow_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    idempotency_key = f"idemp_{uuid.uuid4()}"
    mock_db = AsyncMock()

    req = PaymentConfirmationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        purchase_workflow_id=workflow_id,
        hitl_approval_id=approval_id,
        idempotency_key=idempotency_key,
    )

    # 1. First execution creates Razorpay test order
    res1 = await orchestrator.execute_confirmed_payment(
        db=mock_db,
        request=req,
        amount=Decimal("47990.00"),
        currency="INR",
        product_name="Lenovo IdeaPad Slim 3 Laptop",
    )

    assert res1.status == "SUCCESS"
    assert res1.razorpay_order_id.startswith("order_rzp_")
    assert res1.razorpay_payment_id.startswith("pay_rzp_")
    assert res1.signature_verified is True
    assert res1.amount_paid == Decimal("47990.00")

    # 2. Retry execution with SAME idempotency key returns identical cached response without creating a new payment
    res2 = await orchestrator.execute_confirmed_payment(
        db=mock_db,
        request=req,
        amount=Decimal("47990.00"),
        currency="INR",
        product_name="Lenovo IdeaPad Slim 3 Laptop",
    )

    assert res2.transaction_id == res1.transaction_id
    assert res2.razorpay_order_id == res1.razorpay_order_id
    assert res2.razorpay_payment_id == res1.razorpay_payment_id
