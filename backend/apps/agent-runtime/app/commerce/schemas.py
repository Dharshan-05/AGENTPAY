"""Agentic Commerce Pydantic Schemas for AGENTPAY (Razorpay Buildathon Track 01)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Specifications(BaseModel):
    """Detailed hardware/product technical specifications."""

    cpu: str | None = Field(default=None, description="Processor details e.g. Intel Core i5-1235U / AMD Ryzen 5 5500U")
    ram: str | None = Field(default=None, description="RAM memory e.g. 8GB DDR4 / 16GB LPDDR5")
    storage: str | None = Field(default=None, description="Storage e.g. 512GB NVMe SSD")
    display: str | None = Field(default=None, description="Display e.g. 15.6 inch FHD IPS 250 nits")
    gpu: str | None = Field(default=None, description="Graphics processing unit")
    battery_life: str | None = Field(default=None, description="Battery capacity or runtime")
    os: str | None = Field(default=None, description="Operating system e.g. Windows 11 Home")
    weight_kg: float | None = Field(default=None, description="Weight in kilograms")


class SellerInfo(BaseModel):
    """Normalized seller metadata."""

    seller_id: str = Field(..., description="Unique seller identifier")
    seller_name: str = Field(..., description="Business name of seller")
    seller_rating: float | None = Field(default=None, ge=0.0, le=5.0, description="Customer rating out of 5")
    seller_reputation: str = Field(default="UNKNOWN", description="Reputation badge")
    review_count: int | None = Field(default=None, ge=0, description="Total verified reviews")
    seller_url: str | None = Field(default=None, description="Verified seller page link")
    return_policy: str = Field(default="UNKNOWN", description="Return protection policy")
    warranty_offered: str = Field(default="UNKNOWN", description="Warranty terms")
    availability: str = Field(default="IN_STOCK", description="Stock status")
    seller_risk_score: float | None = Field(default=None, ge=0.0, le=100.0, description="Risk score (0=Safe, 100=Fraud)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"] = Field(default="UNKNOWN", description="Risk level")
    risk_factors: list[str] = Field(default_factory=list, description="Risk signals or warnings")


class NormalizedProduct(BaseModel):
    """Canonical normalized product model for multi-source commerce discovery."""

    product_id: str = Field(..., description="Deterministic product ID")
    product_name: str = Field(..., description="Full product title")
    brand: str = Field(..., description="Brand name e.g. Acer, Lenovo, HP, ASUS, Dell")
    category: str = Field(default="SMARTPHONE", description="Product category")
    description: str = Field(default="", description="Product highlights & summary")
    price: Decimal = Field(..., ge=Decimal("0.00"), description="Current price")
    currency: str = Field(default="INR", description="ISO 4217 currency code")
    original_price: Decimal | None = Field(default=None, description="MSRP or pre-discount price")
    discount_percent: float | None = Field(default=None, ge=0.0, le=100.0, description="Discount percentage")
    rating: float | None = Field(default=None, ge=0.0, le=5.0, description="Product rating out of 5")
    review_count: int | None = Field(default=None, ge=0, description="Review count")
    specifications: Specifications = Field(default_factory=Specifications, description="Hardware specs")
    availability: bool = Field(default=True, description="Stock availability flag")
    seller: SellerInfo = Field(..., description="Associated seller metadata")
    warranty: str = Field(default="UNKNOWN")
    return_policy: str = Field(default="UNKNOWN")
    delivery_info: str = Field(default="Standard Delivery")
    image_url: str | None = Field(default=None, description="Product image URL")
    source: str = Field(default="Live Online Marketplace Provider", description="Data source provenance")
    source_url: str | None = Field(default=None, description="Product page link")
    data_status: Literal["LIVE", "CACHED", "DEMO"] = Field(default="LIVE", description="Data provenance status")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

    # Deterministic Recommendation Ranking Attributes
    rank: int | None = Field(default=None, description="Recommendation rank (1..4)")
    overall_score: float | None = Field(default=None, description="Calculated composite score (0.0-10.0)")
    why_ranked: list[str] = Field(default_factory=list, description="Reasons for this rank derived from specs")
    strengths: list[str] = Field(default_factory=list, description="Key pros and hardware highlights")
    tradeoffs: list[str] = Field(default_factory=list, description="Key cons or trade-offs")

    @property
    def title(self) -> str:
        """Alias for product_name."""
        return self.product_name

    @property
    def mrp(self) -> Decimal | None:
        """Alias for original_price."""
        return self.original_price or self.price

    @property
    def product_url(self) -> str | None:
        """Alias for source_url."""
        return self.source_url


class ComparisonFactorScore(BaseModel):
    """Comparison metric breakdown score for a product."""

    product_id: str
    price_score: float = Field(ge=0.0, le=100.0, description="Price attractiveness score")
    performance_score: float = Field(ge=0.0, le=100.0, description="Performance specs score")
    value_score: float = Field(ge=0.0, le=100.0, description="Overall price-to-performance value score")
    seller_trust_score: float = Field(ge=0.0, le=100.0, description="Seller credibility score")
    risk_score: float = Field(ge=0.0, le=100.0, description="Product risk score")
    overall_score: float = Field(ge=0.0, le=100.0, description="Composite recommendation score")


class ProductComparisonMatrix(BaseModel):
    """Structured product comparison matrix."""

    products: list[NormalizedProduct]
    scores: list[ComparisonFactorScore]
    best_overall_id: str
    best_value_id: str
    best_performance_id: str
    lowest_risk_id: str
    comparison_summary: str


class CommerceSearchRequest(BaseModel):
    """Natural language product search request."""

    prompt: str = Field(..., min_length=1, max_length=2048, description="User prompt or intent string")
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    max_price: Decimal | None = Field(default=None, description="Budget cap override")
    currency: str = Field(default="INR", description="Preferred currency")
    purpose: str | None = Field(default=None, description="Intended usage e.g. coding, gaming, office")
    model: str | None = Field(default=None, description="Target AI model e.g. auto, deepseek/deepseek-r1-distill-llama-70b")


class CommerceSearchResponse(BaseModel):
    """Structured response for product discovery & comparison."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    intent: str = Field(default="PRODUCT_SEARCH")
    category: str = Field(default="ALL")
    budget: Decimal | None = None
    currency: str = "INR"
    query: dict[str, Any] | None = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    products_discovered_count: int = 0
    products: list[NormalizedProduct] = Field(default_factory=list)
    comparison_matrix: ProductComparisonMatrix | None = None
    recommended_product: NormalizedProduct | None = None
    recommendation_rationale: str | None = None
    seller_analysis: dict[str, Any] | None = None
    price_analysis: dict[str, Any] | None = None
    risk_analysis: dict[str, Any] | None = None
    recommendation: dict[str, Any] | None = None
    provider: dict[str, Any] | None = None
    formatted_response: str | None = None
    conversation_context: dict[str, Any] | None = None
    data_status: Literal["LIVE", "CACHED", "DEMO", "UNAVAILABLE"] = Field(default="LIVE")
    provider_status: str = Field(default="ONLINE")
    error_message: str | None = None
    execution_status: str = Field(default="NOT_REQUESTED")
    prompt_security_blocked: bool = False
    latency_ms: float = 0.0


class SellerAnalysisRequest(BaseModel):
    """Request for seller risk & reputation analysis."""

    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    seller_id: str | None = None
    seller_name: str | None = None


class SellerAnalysisResponse(BaseModel):
    """Seller risk analysis response."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    seller_info: SellerInfo
    reputation_summary: str
    risk_level: str
    risk_factors: list[str]
    is_safe_for_transaction: bool


class PurchaseWorkflowRequest(BaseModel):
    """Request to initiate or revalidate a product purchase workflow."""

    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    product_id: str
    product_name: str
    price: Decimal
    currency: str = "INR"
    seller_id: str
    quantity: int = Field(default=1, ge=1)
    user_confirmed_price: Decimal | None = None
    idempotency_key: str | None = None


class PurchaseWorkflowResponse(BaseModel):
    """Result payload of bounded purchase workflow."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    purchase_workflow_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    product: NormalizedProduct
    requested_price: Decimal
    revalidated_price: Decimal
    price_changed: bool = False
    price_change_message: str | None = None
    
    # Policy and Security Decisions
    agentguard_status: str = "ALLOWED"
    fraudguard_risk_score: float = 5.0
    fraudguard_risk_level: str = "LOW"
    fraudguard_xai_reasons: list[str] = Field(default_factory=list)
    hitl_required: bool = True
    hitl_approval_id: uuid.UUID | None = None
    
    # Final Execution State
    workflow_status: Literal["PENDING_HITL", "AUTHORIZED", "PRICE_MISMATCH", "DENIED", "COMPLETED"] = "PENDING_HITL"
    final_execution_decision: str = "REVIEW"
    
    # Razorpay Order Payload (when authorized)
    razorpay_order_id: str | None = None
    razorpay_checkout_config: dict[str, Any] | None = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    latency_ms: float = 0.0


class PaymentConfirmationRequest(BaseModel):
    """Confirmation request after HITL approval to finalize Razorpay test payment."""

    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    purchase_workflow_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    hitl_approval_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_id: str | None = Field(default=None, description="Razorpay payment ID from test checkout UI")
    signature: str | None = Field(default=None, description="Razorpay signature from test checkout UI")


class PaymentConfirmationResponse(BaseModel):
    """Response returned upon completing bounded Razorpay test-mode payment."""

    transaction_id: str
    purchase_workflow_id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    status: str = "SUCCESS"
    amount_paid: Decimal
    currency: str = "INR"
    razorpay_order_id: str
    razorpay_payment_id: str
    signature_verified: bool = True
    audit_event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    completed_at: datetime = Field(default_factory=datetime.utcnow)
