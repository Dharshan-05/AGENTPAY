"""Seller & Dealer Intelligence Service for AGENTPAY Commerce."""

from __future__ import annotations

import logging
from decimal import Decimal

from app.commerce.schemas import NormalizedProduct, SellerAnalysisResponse, SellerInfo

logger = logging.getLogger("agentpay.commerce.services.seller_intelligence")


class SellerIntelligenceService:
    """Evaluates seller reputation, price anomaly, warranty protection, and risk signals."""

    def analyze_seller(
        self,
        seller_info: SellerInfo,
        product: NormalizedProduct | None = None,
        market_average_price: Decimal | None = None,
    ) -> SellerAnalysisResponse:
        """Perform comprehensive seller intelligence & risk evaluation."""
        risk_factors: list[str] = list(seller_info.risk_factors)
        risk_score = seller_info.seller_risk_score

        # Price Anomaly Signal Detection (e.g. price > 50% below market average)
        if product and market_average_price and market_average_price > Decimal("0.00"):
            price_ratio = product.price / market_average_price
            if price_ratio < Decimal("0.50"):
                risk_factors.append("PRICE_ANOMALY: Product price >50% below market average listing.")
                risk_score += 40.0
            elif price_ratio < Decimal("0.70"):
                risk_factors.append("PRICE_DISCOUNT_SUSPICIOUS: Deep discount relative to category benchmark.")
                risk_score += 15.0

        # Seller Rating & Review Count Analysis
        if seller_info.seller_rating < 3.5:
            risk_factors.append("LOW_RATING: Seller rating is below acceptable threshold (3.5/5.0).")
            risk_score += 30.0

        if seller_info.review_count < 20:
            risk_factors.append("UNVERIFIED_HISTORY: Seller has fewer than 20 verified transaction reviews.")
            risk_score += 20.0

        # Return & Warranty Policy Check
        if "no return" in seller_info.return_policy.lower() or "none" in seller_info.return_policy.lower():
            risk_factors.append("NO_RETURN_PROTECTION: Seller offers no return or refund guarantee.")
            risk_score += 25.0

        risk_score = min(risk_score, 100.0)

        # Categorize Risk Level
        if risk_score >= 60.0:
            risk_level = "HIGH"
            is_safe = False
        elif risk_score >= 25.0:
            risk_level = "MEDIUM"
            is_safe = True
        else:
            risk_level = "LOW"
            is_safe = True

        reputation_summary = (
            f"Seller '{seller_info.seller_name}' ({seller_info.seller_reputation}) "
            f"has a rating of {seller_info.seller_rating}/5.0 based on {seller_info.review_count} reviews. "
            f"Return Policy: '{seller_info.return_policy}'. Warranty: '{seller_info.warranty_offered}'."
        )

        return SellerAnalysisResponse(
            seller_info=seller_info.model_copy(
                update={
                    "seller_risk_score": round(risk_score, 1),
                    "risk_level": risk_level,
                    "risk_factors": risk_factors,
                }
            ),
            reputation_summary=reputation_summary,
            risk_level=risk_level,
            risk_factors=risk_factors,
            is_safe_for_transaction=is_safe,
        )
