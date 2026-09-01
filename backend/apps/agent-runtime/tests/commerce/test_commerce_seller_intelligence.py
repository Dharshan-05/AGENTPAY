"""Unit Tests for Seller Intelligence & Price Anomaly Detection (Buildathon Track 01)."""

from decimal import Decimal
import pytest

from app.commerce.schemas import NormalizedProduct, SellerInfo, Specifications
from app.commerce.services.seller_intelligence_service import SellerIntelligenceService


def test_seller_intelligence_verified_seller():
    """Verify low risk rating for verified official brand store."""
    service = SellerIntelligenceService()
    seller = SellerInfo(
        seller_id="seller_lenovo_official",
        seller_name="Lenovo Official Store",
        seller_rating=4.8,
        seller_reputation="VERIFIED_BRAND_STORE",
        review_count=15000,
        return_policy="7-Day Replacement Guarantee",
        warranty_offered="1 Year Brand Warranty",
        seller_risk_score=5.0,
        risk_level="LOW",
    )

    res = service.analyze_seller(seller_info=seller)

    assert res.risk_level == "LOW"
    assert res.is_safe_for_transaction is True
    assert "Lenovo Official Store" in res.reputation_summary


def test_seller_intelligence_price_anomaly_detection():
    """Verify deep price anomaly (>50% below market average) triggers risk warning."""
    service = SellerIntelligenceService()
    seller = SellerInfo(
        seller_id="seller_unknown",
        seller_name="Discount Warehouse",
        seller_rating=4.0,
        seller_reputation="UNVERIFIED",
        review_count=50,
        return_policy="No Returns",
        warranty_offered="None",
        seller_risk_score=20.0,
    )
    product = NormalizedProduct(
        product_id="prod_fake",
        product_name="Fake Ultra Laptop",
        brand="Unknown",
        category="LAPTOP",
        description="Suspicious listing",
        price=Decimal("15000.00"),
        currency="INR",
        seller=seller,
    )

    res = service.analyze_seller(
        seller_info=seller,
        product=product,
        market_average_price=Decimal("50000.00"),
    )

    assert res.seller_info.seller_risk_score >= 60.0
    assert res.risk_level in ("HIGH", "CRITICAL")
    assert any("PRICE_ANOMALY" in rf for rf in res.risk_factors)
