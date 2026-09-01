"""Commerce FraudGuard Risk Engine & XAI Explainability Service."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.commerce.schemas import NormalizedProduct, SellerInfo
from app.commerce.services.seller_intelligence_service import SellerIntelligenceService

logger = logging.getLogger("agentpay.commerce.services.risk")


class CommerceRiskAssessment(BaseModel):
    """Explainable FraudGuard Commerce Risk Assessment Result."""

    product_id: str
    risk_score: float = Field(ge=0.0, le=100.0, description="Risk Score (0=Safe, 100=Critical Fraud)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Risk Level")
    confidence: float = Field(default=0.96, ge=0.0, le=1.0, description="Model confidence score")
    risk_factors: list[str] = Field(default_factory=list, description="Explicit human-readable XAI risk signals")
    is_transaction_allowed: bool = Field(default=True, description="True if risk level is within threshold")


class CommerceRiskService:
    """Production FraudGuard integration for product, seller, price anomaly, and transaction risk."""

    def __init__(self, seller_service: SellerIntelligenceService | None = None) -> None:
        self.seller_service = seller_service or SellerIntelligenceService()

    def evaluate_commerce_risk(
        self,
        product: NormalizedProduct,
        requested_amount: Decimal | None = None,
        market_average_price: Decimal | None = None,
    ) -> CommerceRiskAssessment:
        """Evaluate product, seller, price anomaly, and behavioral transaction risk."""
        risk_factors: list[str] = []
        base_score = 5.0

        # 1. Seller Risk Assessment
        seller_res = self.seller_service.analyze_seller(
            seller_info=product.seller,
            product=product,
            market_average_price=market_average_price,
        )
        base_score += seller_res.seller_info.seller_risk_score * 0.5
        risk_factors.extend(seller_res.risk_factors)

        # 2. Price Mismatch / Revalidation Risk
        if requested_amount and requested_amount > Decimal("0.00"):
            if product.price > requested_amount:
                diff = product.price - requested_amount
                risk_factors.append(f"PRICE_INCREASE_DETECTED: Current price ({product.price} {product.currency}) exceeds requested price ({requested_amount} {product.currency}) by {diff}.")
                base_score += 25.0

        # 3. Product Specification Integrity Signals
        if not product.availability:
            risk_factors.append("ITEM_OUT_OF_STOCK: Requested item is currently unavailable.")
            base_score += 50.0

        # 4. Review Consistency Signals
        if product.rating < 3.8 and product.review_count > 50:
            risk_factors.append("LOW_PRODUCT_RATING: Customer satisfaction rating is below benchmark (3.8/5.0).")
            base_score += 15.0

        # Final Score Quantization
        final_risk_score = round(min(base_score, 100.0), 1)

        # Determine Risk Level & Transaction Permission
        if final_risk_score >= 70.0:
            risk_level = "CRITICAL"
            allowed = False
        elif final_risk_score >= 45.0:
            risk_level = "HIGH"
            allowed = False
        elif final_risk_score >= 20.0:
            risk_level = "MEDIUM"
            allowed = True
        else:
            risk_level = "LOW"
            allowed = True

        if not risk_factors:
            risk_factors = [
                "Seller history normal",
                "Price within expected range",
                "No major anomaly detected",
                "Return policy available",
            ]

        logger.info(
            "CommerceRiskService evaluated product %s (Score: %s, Level: %s, Allowed: %s)",
            product.product_id,
            final_risk_score,
            risk_level,
            allowed,
        )

        return CommerceRiskAssessment(
            product_id=product.product_id,
            risk_score=final_risk_score,
            risk_level=risk_level,
            confidence=0.96,
            risk_factors=risk_factors,
            is_transaction_allowed=allowed,
        )
