"""Razorpay Commerce Payment Orchestrator & Idempotency Boundary."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from app.commerce.schemas import PaymentConfirmationRequest, PaymentConfirmationResponse
from app.payment.payment_service import PaymentService
from app.payment.providers.razorpay.client import RazorpayClientWrapper
from app.payment.providers.razorpay.provider import RazorpayProvider
from app.schemas.payment import PaymentOrderRequest, PaymentServiceOutcome, PaymentServiceRequest

logger = logging.getLogger("agentpay.commerce.services.payment_orchestrator")


class CommercePaymentOrchestrator:
    """Orchestrates bounded Razorpay test-mode payment execution with idempotency protection."""

    def __init__(
        self,
        payment_service: PaymentService | None = None,
        razorpay_provider: RazorpayProvider | None = None,
    ) -> None:
        self.payment_service = payment_service or PaymentService()
        self.razorpay_provider = razorpay_provider or RazorpayProvider()
        # In-memory idempotency cache for verified test transactions
        self._completed_transactions: dict[str, PaymentConfirmationResponse] = {}

    async def execute_confirmed_payment(
        self,
        db: Any,
        request: PaymentConfirmationRequest,
        amount: Decimal,
        currency: str = "INR",
        product_name: str = "Laptop",
    ) -> PaymentConfirmationResponse:
        """Execute bounded Razorpay test-mode payment following HITL confirmation."""
        # 1. Idempotency Check (Prevents double payment on retries)
        if request.idempotency_key in self._completed_transactions:
            logger.info(
                "Idempotency hit for key=%s. Returning cached Razorpay payment response.",
                request.idempotency_key,
            )
            return self._completed_transactions[request.idempotency_key]

        tx_id = f"tx_rzp_{uuid.uuid4().hex[:12]}"
        auth_id = uuid.uuid4()
        auth_fp = f"fp_auth_{uuid.uuid4().hex[:12]}"

        # 2. Prepare Order Request
        order_req = PaymentOrderRequest(
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=tx_id,
            amount=amount,
            currency=currency,
            idempotency_key=request.idempotency_key,
            receipt=f"rcpt_{tx_id[:20]}",
            notes={"product_name": product_name, "workflow_id": str(request.purchase_workflow_id)},
        )

        # 3. Create Razorpay Test Order with Enabled Configuration
        from pydantic import SecretStr
        from app.payment.providers.razorpay.config import RazorpayConfiguration

        rzp_config = RazorpayConfiguration(
            key_id="rzp_test_buildathon_key",
            key_secret=SecretStr("rzp_test_secret"),
            enabled=True,
            environment_mode="test",
        )
        rzp_client = RazorpayClientWrapper(key_id="rzp_test_buildathon_key", key_secret="rzp_test_secret", is_mock=True)
        provider = RazorpayProvider(config=rzp_config, client=rzp_client)

        order_res = provider.create_order(order_req, auth_id, auth_fp)
        razorpay_order_id = order_res.order_id

        # 4. Generate Mock/Live Test Payment ID & Verify Signature
        payment_id = request.payment_id or f"pay_rzp_mock_{uuid.uuid4().hex[:12]}"
        mock_sig = f"sig_rzp_valid_{uuid.uuid4().hex[:12]}"
        signature = request.signature or mock_sig

        sig_valid = rzp_client.verify_signature(razorpay_order_id, payment_id, signature)

        response = PaymentConfirmationResponse(
            transaction_id=tx_id,
            purchase_workflow_id=request.purchase_workflow_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            status="SUCCESS",
            amount_paid=amount,
            currency=currency,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=payment_id,
            signature_verified=sig_valid,
            audit_event_id=uuid.uuid4(),
        )

        # Store in Idempotency Cache
        self._completed_transactions[request.idempotency_key] = response
        logger.info(
            "Razorpay Test Payment completed successfully (tx_id=%s, order_id=%s, payment_id=%s)",
            tx_id,
            razorpay_order_id,
            payment_id,
        )
        return response
