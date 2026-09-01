"""FastAPI Router for Agentic Commerce Endpoints (Razorpay Buildathon Track 01)."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session
from app.commerce.schemas import (
    CommerceSearchRequest,
    CommerceSearchResponse,
    PaymentConfirmationRequest,
    PaymentConfirmationResponse,
    PurchaseWorkflowRequest,
    PurchaseWorkflowResponse,
    SellerAnalysisRequest,
    SellerAnalysisResponse,
)
from app.commerce.services.commerce_facade_service import CommerceFacadeService

logger = logging.getLogger("agentpay.api.v1.commerce")

router = APIRouter(prefix="/commerce", tags=["Agentic Commerce"])
_facade_service = CommerceFacadeService()


@router.post("/search", response_model=CommerceSearchResponse, status_code=status.HTTP_200_OK)
async def search_and_compare_products(
    request: CommerceSearchRequest,
    db: AsyncSession = Depends(get_db_session),
) -> CommerceSearchResponse:
    """Discover, compare, and rank online products from natural language prompts."""
    try:
        return await _facade_service.execute_commerce_search(db=db, request=request)
    except Exception as exc:
        logger.error("Commerce search endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute product discovery and comparison.",
        ) from exc


@router.post("/seller-analysis", response_model=SellerAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_seller_reputation(
    request: SellerAnalysisRequest,
) -> SellerAnalysisResponse:
    """Analyze seller reputation, price anomaly, and risk signals."""
    try:
        return await _facade_service.analyze_seller(request=request)
    except Exception as exc:
        logger.error("Seller analysis endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze seller reputation.",
        ) from exc


@router.post("/purchase", response_model=PurchaseWorkflowResponse, status_code=status.HTTP_200_OK)
async def initiate_purchase_request(
    request: PurchaseWorkflowRequest,
    db: AsyncSession = Depends(get_db_session),
) -> PurchaseWorkflowResponse:
    """Initiate bounded purchase request & policy evaluation with price revalidation."""
    try:
        return await _facade_service.initiate_purchase(db=db, request=request)
    except Exception as exc:
        logger.error("Initiate purchase endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate purchase workflow.",
        ) from exc


@router.post("/confirm-payment", response_model=PaymentConfirmationResponse, status_code=status.HTTP_200_OK)
async def confirm_and_pay(
    request: PaymentConfirmationRequest,
    amount: Decimal = Decimal("47990.00"),
    currency: str = "INR",
    product_name: str = "Lenovo IdeaPad Slim 3 Laptop",
    db: AsyncSession = Depends(get_db_session),
) -> PaymentConfirmationResponse:
    """Confirm HITL approval & execute bounded Razorpay test-mode payment."""
    try:
        return await _facade_service.confirm_and_pay(
            db=db,
            request=request,
            amount=amount,
            currency=currency,
            product_name=product_name,
        )
    except Exception as exc:
        logger.error("Payment confirmation endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute Razorpay test-mode payment.",
        ) from exc
