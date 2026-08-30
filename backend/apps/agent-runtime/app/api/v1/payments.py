"""FastAPI Payment Webhook Router Boundary (Phase 293–294)."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.payment.webhooks.razorpay_webhook import RazorpayWebhookHandler
from app.schemas.payment_webhook import UntrustedWebhookRequest, WebhookIngestionResult

logger = logging.getLogger("agentpay.api.v1.payments")

payments_router = APIRouter(prefix="/payments", tags=["Payments"])

_webhook_handler = RazorpayWebhookHandler()


@payments_router.post(
    "/webhooks/razorpay",
    response_model=WebhookIngestionResult,
    status_code=status.HTTP_200_OK,
    summary="Razorpay Webhook Ingestion & Signature Verification Boundary (Phase 293–294)",
    description=(
        "Receives raw Razorpay webhook HTTP body, performs HMAC-SHA256 signature verification "
        "before JSON parsing, constructs a trusted envelope, and returns safe acknowledgement. "
        "DOES NOT mutate payment status or execute business event processing (Phase 295)."
    ),
)
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> WebhookIngestionResult:
    """Ingest raw Razorpay webhook and cryptographically verify signature (Phase 293–294).

    Signature verification operates on the EXACT raw HTTP request body bytes before JSON parsing.
    """
    if not x_razorpay_signature or not x_razorpay_signature.strip():
        logger.warning("Webhook endpoint request rejected: Missing X-Razorpay-Signature header.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required X-Razorpay-Signature header.",
        )

    # 1. Read exact raw HTTP body bytes
    raw_body = await request.body()

    # 2. Resolve optional tenant_id UUID context
    tenant_uuid: uuid.UUID | None = None
    if x_tenant_id and x_tenant_id.strip():
        try:
            tenant_uuid = uuid.UUID(x_tenant_id.strip())
        except ValueError:
            logger.warning("Invalid X-Tenant-ID header format in webhook request.")

    untrusted_req = UntrustedWebhookRequest(
        raw_body=raw_body,
        signature=x_razorpay_signature.strip(),
        tenant_id=tenant_uuid,
        provider_name="razorpay",
    )

    # 3. Process via RazorpayWebhookHandler
    ingest_res, envelope = _webhook_handler.process_webhook(untrusted_req)

    # 4. Handle HTTP failure status codes
    if ingest_res.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ingest_res.message,
        )

    if ingest_res.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ingest_res.message,
        )

    return ingest_res
