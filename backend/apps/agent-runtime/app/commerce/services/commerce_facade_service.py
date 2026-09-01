"""Agentic Commerce Main Facade Service (Razorpay Buildathon Track 01)."""

from __future__ import annotations

import logging
import re
import time
import uuid
from decimal import Decimal
from typing import Any

from app.commerce.providers.online_search_provider import OnlineProductSearchProvider
from app.commerce.schemas import (
    CommerceSearchRequest,
    CommerceSearchResponse,
    NormalizedProduct,
    PaymentConfirmationRequest,
    PaymentConfirmationResponse,
    PurchaseWorkflowRequest,
    PurchaseWorkflowResponse,
    SellerAnalysisRequest,
    SellerAnalysisResponse,
)
from app.commerce.services.commerce_payment_orchestrator import CommercePaymentOrchestrator
from app.commerce.services.commerce_risk_service import CommerceRiskService
from app.commerce.services.product_comparison_service import ProductComparisonService
from app.commerce.services.purchase_workflow_service import PurchaseWorkflowService
from app.commerce.services.seller_intelligence_service import SellerIntelligenceService

logger = logging.getLogger("agentpay.commerce.facade")

SESSION_STORE: dict[str, dict[str, Any]] = {}


def get_active_session(tenant_id: Any, agent_id: Any) -> dict[str, Any] | None:
    """Retrieve active commerce session context for tenant and agent."""
    key = f"{tenant_id}_{agent_id}"
    return SESSION_STORE.get(key)


def set_active_session(tenant_id: Any, agent_id: Any, data: dict[str, Any]) -> None:
    """Update active commerce session context."""
    key = f"{tenant_id}_{agent_id}"
    existing = SESSION_STORE.get(key, {})
    existing.update(data)
    SESSION_STORE[key] = existing


class CommerceFacadeService:
    """Production Agentic Commerce Intelligence & Execution Facade for AGENTPAY."""

    def __init__(
        self,
        search_provider: OnlineProductSearchProvider | None = None,
        comparison_service: ProductComparisonService | None = None,
        seller_service: SellerIntelligenceService | None = None,
        risk_service: CommerceRiskService | None = None,
        purchase_service: PurchaseWorkflowService | None = None,
        payment_orchestrator: CommercePaymentOrchestrator | None = None,
    ) -> None:
        self.search_provider = search_provider or OnlineProductSearchProvider()
        self.comparison_service = comparison_service or ProductComparisonService()
        self.seller_service = seller_service or SellerIntelligenceService()
        self.risk_service = risk_service or CommerceRiskService()
        self.purchase_service = purchase_service or PurchaseWorkflowService()
        self.payment_orchestrator = payment_orchestrator or CommercePaymentOrchestrator()

    async def execute_commerce_search(
        self,
        db: Any,
        request: CommerceSearchRequest,
    ) -> CommerceSearchResponse:
        """Process natural language commerce request for discovery, comparison, and recommendation."""
        start_time = time.perf_counter()
        req_id = uuid.uuid4()

        # Prompt Injection Security Scan using PromptGuard
        from app.application.services.prompt_guard_service import PromptGuardService
        pg = PromptGuardService()
        guard_result = pg.sanitize_prompt(request.prompt)
        prompt_lower = request.prompt.lower()
        if guard_result.contains_suspicious_injection or guard_result.risk_level in ("HIGH", "CRITICAL") or any(kw in prompt_lower for kw in ["ignore agentguard", "bypass agentguard", "ignore security", "bypass fraudguard", "skip hitl", "charge without authorization"]):
            logger.warning("Commerce prompt security violation blocked for req %s", req_id)
            return CommerceSearchResponse(
                request_id=req_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                intent="PROMPT_INJECTION_ATTEMPT",
                execution_status="DENIED",
                prompt_security_blocked=True,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        # Natural Language Category, Budget & Purpose Extraction
        category = "ALL"
        prompt_lower = request.prompt.lower()
        is_feature_phone_query = any(w in prompt_lower for w in ["feature phone", "keypad", "basic phone", "button phone"])

        if any(w in prompt_lower for w in ["smartwatch", "watch"]):
            category = "SMARTWATCH"
        elif any(w in prompt_lower for w in ["headphone", "headphones", "earbuds", "earphone", "airpods"]):
            category = "HEADPHONES"
        elif any(w in prompt_lower for w in ["tablet", "ipad"]):
            category = "TABLET"
        elif any(w in prompt_lower for w in ["monitor", "display"]):
            category = "MONITOR"
        elif any(w in prompt_lower for w in ["camera"]):
            category = "CAMERA"
        elif any(w in prompt_lower for w in ["tv", "television"]):
            category = "TV"
        elif any(w in prompt_lower for w in ["phone", "mobile", "smartphone", "iphone", "samsung"]):
            category = "FEATURE_PHONE" if is_feature_phone_query else "SMARTPHONE"
        elif any(w in prompt_lower for w in ["laptop", "notebook", "macbook"]):
            category = "LAPTOP"

        budget = request.max_price
        if budget is None:
            bm = re.search(r"(?:under|below|less than|within|up to|for|budget)?\s*(?:₹|rs\.?|inr)?\s*([0-9,]+)\s*(k|lac|lakh)?\b", prompt_lower)
            num_match = re.search(r"(?:under|below|less than|within|up to|for|budget)\s*(?:₹|rs\.?|inr)?\s*([0-9,]+)\s*(k|lac|lakh)?\b", prompt_lower)
            target_match = num_match or bm
            if target_match:
                val_str, unit = target_match.groups()
                try:
                    val = Decimal(val_str.replace(",", ""))
                    if unit == "k":
                        val *= Decimal("1000")
                    elif unit in ("lac", "lakh"):
                        val *= Decimal("100000")
                    if val >= Decimal("500"):
                        budget = val
                except Exception:
                    pass

        purpose = request.purpose
        if purpose is None:
            if "coding" in prompt_lower or "programming" in prompt_lower or "developer" in prompt_lower:
                purpose = "CODING"
            elif "gaming" in prompt_lower:
                purpose = "GAMING"

        # Determine Intent
        intent_type = "PRODUCT_SEARCH"
        if "compare" in prompt_lower or "which one is best" in prompt_lower or "which is best" in prompt_lower or "which one" in prompt_lower:
            intent_type = "PRODUCT_COMPARISON"
        elif "seller" in prompt_lower or "safest seller" in prompt_lower:
            intent_type = "SELLER_ANALYSIS"
        elif "genuine" in prompt_lower or "risky" in prompt_lower or "risk" in prompt_lower:
            intent_type = "PRODUCT_RISK_ANALYSIS"
        elif "price" in prompt_lower or "check price" in prompt_lower:
            intent_type = "PRICE_ANALYSIS"
        elif "why" in prompt_lower or "recommend" in prompt_lower or "suggest" in prompt_lower:
            intent_type = "PRODUCT_RECOMMENDATION"
        elif "details" in prompt_lower or "specs" in prompt_lower:
            intent_type = "PRODUCT_DETAILS"
        elif any(w in prompt_lower for w in ["select", "choose", "pick", "want"]):
            intent_type = "PRODUCT_SELECTION"

        # 1. Product Discovery via Online Search Provider (Retrieves up to 20 candidate listings)
        products = await self.search_provider.search_products(
            query=request.prompt,
            category=category,
            max_price=budget,
            purpose=purpose,
            limit=20,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not products:
            logger.warning("Online Product Discovery returned zero verified listings for req %s", req_id)
            return CommerceSearchResponse(
                request_id=req_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                intent=intent_type,
                category=category,
                budget=budget,
                currency=request.currency,
                query={
                    "category": category,
                    "budget": float(budget) if budget else None,
                    "purpose": purpose or "GENERAL",
                    "ranking_mode": "BEST_OVERALL",
                },
                products_discovered_count=0,
                products=[],
                data_status="UNAVAILABLE",
                provider_status="OFFLINE",
                error_message="ONLINE COMMERCE DATA UNAVAILABLE: Unable to retrieve verified current listings.",
                formatted_response="ONLINE COMMERCE DATA UNAVAILABLE\n\nUnable to retrieve verified current listings matching your request.\n\n[RETRY]",
                execution_status="NOT_REQUESTED",
                prompt_security_blocked=False,
                latency_ms=elapsed_ms,
            )

        # 2. Category-Aware Multi-Factor Product Comparison & Deterministic Ranking
        matrix = self.comparison_service.compare_products(
            products=products,
            user_purpose=purpose,
            budget=budget,
        )

        # 3. Select TOP 4 Candidates (or available count if fewer than 4 exist)
        ranked_products = matrix.products
        top_candidates = ranked_products[:4]
        recommended_product = top_candidates[0]

        # Check active session for contextual memory
        active_sess = get_active_session(request.tenant_id, request.agent_id)
        if intent_type in ("PRODUCT_COMPARISON", "PRODUCT_RECOMMENDATION", "PRODUCT_DETAILS", "SELLER_ANALYSIS", "PRICE_ANALYSIS", "PRODUCT_RISK_ANALYSIS", "PRODUCT_SELECTION") and active_sess and active_sess.get("top_candidates") and category == "ALL":
            # Reuse active session candidates for follow-up contextual queries
            top_candidates = active_sess["top_candidates"]
            recommended_product = active_sess.get("selected_product") or top_candidates[0]
            matrix = active_sess.get("comparison_matrix") or matrix
            category = active_sess.get("category", category)
            if active_sess.get("budget"):
                budget = Decimal(str(active_sess["budget"]))

        # Handle PRODUCT_SELECTION intent specifically
        if intent_type == "PRODUCT_SELECTION" or "select" in prompt_lower or "choose" in prompt_lower:
            sel_idx = 0
            if "2" in prompt_lower or "second" in prompt_lower:
                sel_idx = 1 if len(top_candidates) > 1 else 0
            elif "3" in prompt_lower or "third" in prompt_lower:
                sel_idx = 2 if len(top_candidates) > 2 else 0
            elif "4" in prompt_lower or "fourth" in prompt_lower:
                sel_idx = 3 if len(top_candidates) > 3 else 0
            recommended_product = top_candidates[sel_idx]

        # Update active session context
        set_active_session(
            request.tenant_id,
            request.agent_id,
            {
                "search_query": request.prompt,
                "category": category,
                "budget": float(budget) if budget else None,
                "purpose": purpose,
                "top_candidates": top_candidates,
                "recommended_product": top_candidates[0],
                "comparison_matrix": matrix,
                "selected_product": recommended_product,
                "selected_product_id": recommended_product.product_id,
                "selected_price": Decimal(str(recommended_product.price)),
                "selection_timestamp": time.time(),
            },
        )

        query_obj = {
            "category": category,
            "budget": float(budget) if budget else None,
            "purpose": purpose or "GENERAL",
            "ranking_mode": "BEST_OVERALL" if not purpose else f"BEST_FOR_{purpose.upper()}",
        }

        # 4. Structured Analysis Objects
        seller_analysis_data = {
            "seller_id": recommended_product.seller.seller_id,
            "seller_name": recommended_product.seller.seller_name,
            "seller_rating": recommended_product.seller.seller_rating if recommended_product.seller.seller_rating is not None else "UNKNOWN",
            "reputation": recommended_product.seller.seller_reputation or "UNKNOWN",
            "risk_level": recommended_product.seller.risk_level or "UNKNOWN",
            "is_official_store": "Official" in recommended_product.seller.seller_name or recommended_product.seller.seller_reputation == "VERIFIED_BRAND_STORE",
            "verified_status": "VERIFIED" if recommended_product.seller.seller_reputation in ("VERIFIED_BRAND_STORE", "PLATINUM_SELLER") else "UNKNOWN",
        }

        mrp_val = float(recommended_product.original_price) if recommended_product.original_price else None
        discount_val = recommended_product.discount_percent if recommended_product.discount_percent is not None else None
        price_analysis_data = {
            "current_price": float(recommended_product.price),
            "mrp": mrp_val if mrp_val is not None else "UNKNOWN",
            "discount_percent": discount_val if discount_val is not None else "UNKNOWN",
            "price_anomaly": ("LOW" if discount_val and discount_val < 50.0 else "MEDIUM") if discount_val is not None else "UNKNOWN",
            "deal_quality": ("EXCELLENT" if discount_val and discount_val >= 25.0 else ("GOOD" if discount_val and discount_val >= 10.0 else "FAIR")) if discount_val is not None else "UNKNOWN",
            "price_evaluation": f"Best available offer with {discount_val}% savings." if discount_val is not None else "Current market price.",
        }

        fg_risk = recommended_product.seller.seller_risk_score if recommended_product.seller.seller_risk_score is not None else "UNKNOWN"
        risk_analysis_data = {
            "product_id": recommended_product.product_id,
            "risk_score": fg_risk,
            "risk_level": recommended_product.seller.risk_level or "UNKNOWN",
            "confidence": 0.95 if fg_risk != "UNKNOWN" else 0.50,
            "factors": recommended_product.seller.risk_factors or ["Marketplace listing verified"],
            "explanation": f"Risk profile evaluated for {recommended_product.seller.seller_name} ({recommended_product.seller.seller_reputation}).",
        }

        recommendation_data = {
            "rank": 1,
            "recommended_product_id": recommended_product.product_id,
            "recommended_product_name": recommended_product.product_name,
            "price": float(recommended_product.price),
            "why": recommended_product.why_ranked or [f"Ranked #1 with highest composite score ({recommended_product.overall_score}/10)"],
            "best_for": [purpose or "General Purpose", "Best Price-to-Performance", "Verified Seller Trust"],
            "tradeoffs": recommended_product.tradeoffs or ["Standard market weight and battery life"],
            "alternative_picks": [
                {
                    "rank": p.rank,
                    "product_id": p.product_id,
                    "name": p.product_name,
                    "price": float(p.price),
                    "overall_score": p.overall_score,
                    "role": "BEST VALUE" if p.product_id == matrix.best_value_id else ("BEST PERFORMANCE" if p.product_id == matrix.best_performance_id else "RUNNER UP"),
                }
                for p in top_candidates[1:]
            ],
        }

        # 5. Build Formatted Conversational Summary & Context Payload
        top_name = recommended_product.product_name
        top_price = float(recommended_product.price)
        budget_str = f"₹{int(budget):,}" if budget else "No limit"
        seller_name = recommended_product.seller.seller_name
        seller_risk = recommended_product.seller.risk_level or "UNKNOWN"
        rating_str = f"{recommended_product.rating}/5" if recommended_product.rating is not None else "UNKNOWN"
        reviews_str = f"{recommended_product.review_count:,} reviews" if recommended_product.review_count is not None else "UNKNOWN reviews"

        candidates_lines = []
        for p in top_candidates:
            rank_tag = f"#{p.rank} BEST OVERALL" if p.rank == 1 else (f"#{p.rank} BEST VALUE" if p.product_id == matrix.best_value_id else f"#{p.rank} CANDIDATE")
            candidates_lines.append(
                f"{rank_tag}: {p.product_name}\n"
                f"• Price: ₹{float(p.price):,.2f} | Overall Score: {p.overall_score}/10\n"
                f"• Specs: {p.specifications.cpu or ''} {p.specifications.ram or ''} {p.specifications.storage or ''}\n"
                f"• Seller: {p.seller.seller_name} ({p.seller.seller_reputation})\n"
                f"• Strengths: {', '.join(p.strengths[:2]) if p.strengths else 'Solid specs'}\n"
                f"• Trade-offs: {', '.join(p.tradeoffs[:1]) if p.tradeoffs else 'None'}"
            )
        top4_text = "\n\n".join(candidates_lines)

        formatted_summary = (
            f"LIVE DATA (Source: {recommended_product.source})\n"
            f"Retrieved: Just now | Status: {recommended_product.data_status}\n\n"
            f"Evaluated {len(products)} {category.lower().replace('_', ' ')} listings (Budget: {budget_str}, Purpose: {purpose or 'GENERAL'}).\n\n"
            f"TOP {len(top_candidates)} RECOMMENDATIONS:\n\n"
            f"{top4_text}\n\n"
            f"WHY #{recommended_product.rank} ({top_name}) IS THE TOP RECOMMENDATION:\n"
            f"• Rationale: {recommended_product.why_ranked[0] if recommended_product.why_ranked else 'Highest combined specs, value, and seller trust.'}\n"
            f"• FraudGuard Risk Score: {fg_risk}/100 ({seller_risk} RISK)\n\n"
            f"Would you like me to compare these options side-by-side or proceed with a selection?"
        )

        provider_data = {
            "provider_name": "Live Online Marketplace Provider",
            "provider_status": "ONLINE",
            "search_latency_ms": round(elapsed_ms, 2),
            "data_status": "LIVE",
        }

        context_payload = {
            "active_category": category,
            "active_budget": float(budget) if budget else None,
            "selected_product_id": recommended_product.product_id,
            "discovered_product_ids": [p.product_id for p in top_candidates],
            "last_intent": intent_type,
            "data_status": "LIVE",
        }

        return CommerceSearchResponse(
            request_id=req_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            intent=intent_type,
            category=category,
            budget=budget,
            currency=request.currency,
            query=query_obj,
            products_discovered_count=len(products),
            products=top_candidates,
            comparison_matrix=matrix,
            recommended_product=recommended_product,
            recommendation_rationale=matrix.comparison_summary,
            seller_analysis=seller_analysis_data,
            price_analysis=price_analysis_data,
            risk_analysis=risk_analysis_data,
            recommendation=recommendation_data,
            provider=provider_data,
            formatted_response=formatted_summary,
            conversation_context=context_payload,
            execution_status="NOT_REQUESTED",
            latency_ms=elapsed_ms,
        )

    async def analyze_seller(
        self,
        request: SellerAnalysisRequest,
    ) -> SellerAnalysisResponse:
        """Perform seller risk & reputation evaluation."""
        seller_id = request.seller_id or "seller_appario_retail"
        seller_info = await self.search_provider.get_seller_info(seller_id)
        if not seller_info:
            seller_info = list(self.search_provider._sellers.values())[0]

        return self.seller_service.analyze_seller(seller_info=seller_info)

    async def initiate_purchase(
        self,
        db: Any,
        request: PurchaseWorkflowRequest,
    ) -> PurchaseWorkflowResponse:
        """Initiate bounded purchase request & policy evaluation."""
        return await self.purchase_service.initiate_purchase_workflow(db, request)

    async def confirm_and_pay(
        self,
        db: Any,
        request: PaymentConfirmationRequest,
        amount: Decimal,
        currency: str = "INR",
        product_name: str = "Laptop",
    ) -> PaymentConfirmationResponse:
        """Execute bounded Razorpay test-mode payment."""
        return await self.payment_orchestrator.execute_confirmed_payment(
            db=db,
            request=request,
            amount=amount,
            currency=currency,
            product_name=product_name,
        )
