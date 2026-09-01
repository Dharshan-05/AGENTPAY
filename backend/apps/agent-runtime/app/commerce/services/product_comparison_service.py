"""Product Comparison & Category-Aware Deterministic Ranking Engine for AGENTPAY Commerce."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from app.commerce.schemas import (
    ComparisonFactorScore,
    NormalizedProduct,
    ProductComparisonMatrix,
)

logger = logging.getLogger("agentpay.commerce.services.product_comparison")


class ProductComparisonService:
    """Multi-factor category-aware product comparison and deterministic scoring engine."""

    def compare_products(
        self,
        products: list[NormalizedProduct],
        user_purpose: str | None = None,
        budget: Decimal | None = None,
    ) -> ProductComparisonMatrix:
        """Generate structured comparative evaluation matrix across discovered products."""
        if not products:
            raise ValueError("Cannot compare empty product list.")

        purpose_upper = (user_purpose or "GENERAL").upper()
        prices = [float(p.price) for p in products]
        min_price = min(prices) if prices else 1.0
        max_price = max(prices) if prices else 1.0

        scores_map: dict[str, ComparisonFactorScore] = {}

        for p in products:
            p_val = float(p.price)

            # 1. Price Attractiveness Score (0-100)
            if max_price == min_price:
                price_score = 90.0
            else:
                price_score = round(100.0 - ((p_val - min_price) / (max_price - min_price)) * 40.0, 1)

            # 2. Category-Aware Specification & Performance Score (0-100)
            cat_upper = p.category.upper()
            perf_score = 50.0
            specs_score = 50.0

            ram_str = (p.specifications.ram or "").lower()
            cpu_str = (p.specifications.cpu or "").lower()
            gpu_str = (p.specifications.gpu or "").lower()
            storage_str = (p.specifications.storage or "").lower()
            display_str = (p.specifications.display or "").lower()

            if cat_upper == "LAPTOP":
                if "32gb" in ram_str:
                    perf_score += 30.0
                elif "16gb" in ram_str:
                    perf_score += 20.0
                elif "8gb" in ram_str:
                    perf_score += 10.0

                if any(c in cpu_str for c in ["i7", "ryzen 7", "m2", "m3", "i9"]):
                    perf_score += 20.0
                elif any(c in cpu_str for c in ["i5", "ryzen 5"]):
                    perf_score += 15.0

                if any(g in gpu_str for g in ["rtx", "gtx", "geforce", "radeon rx"]):
                    if "GAMING" in purpose_upper:
                        perf_score += 40.0
                        specs_score += 25.0
                    else:
                        perf_score += 25.0
                        specs_score += 15.0
                elif "iris" in gpu_str or "radeon" in gpu_str:
                    perf_score += 5.0 if "GAMING" in purpose_upper else 10.0

                if "1tb" in storage_str:
                    specs_score += 20.0
                elif "512gb" in storage_str:
                    specs_score += 10.0

            elif cat_upper in ("SMARTPHONE", "MOBILE_PHONE"):
                if "12gb" in ram_str or "16gb" in ram_str:
                    perf_score += 25.0
                elif "8gb" in ram_str:
                    perf_score += 15.0

                if any(c in cpu_str for c in ["gen 3", "gen 2", "dimensity 9", "exynos 2"]):
                    perf_score += 25.0
                elif any(c in cpu_str for c in ["snapdragon", "dimensity", "exynos"]):
                    perf_score += 15.0

                if "120hz" in display_str or "amoled" in display_str:
                    specs_score += 20.0

                if "256gb" in storage_str or "512gb" in storage_str:
                    specs_score += 15.0

            else:  # SMARTWATCH, HEADPHONES, TABLET, OTHER
                if p.rating is not None and p.rating >= 4.5:
                    perf_score += 25.0
                    specs_score += 25.0

            perf_score = min(perf_score, 100.0)
            specs_score = min(specs_score, 100.0)

            # 3. Rating & Value Score (0-100)
            rating_val = p.rating if p.rating is not None else 4.0
            rating_score = (rating_val / 5.0) * 100.0
            value_score = round(0.4 * price_score + 0.4 * perf_score + 0.2 * rating_score, 1)

            # 4. Seller Trust & Risk Score (0-100)
            seller_rating_val = p.seller.seller_rating if p.seller.seller_rating is not None else 4.0
            seller_trust = (seller_rating_val / 5.0) * 100.0
            risk_val = p.seller.seller_risk_score if p.seller.seller_risk_score is not None else 10.0
            risk_score = round(risk_val, 1)

            # 5. Configurable & Purpose-Driven Composite Score Weights
            if "CODING" in purpose_upper or "PROGRAMMING" in purpose_upper:
                overall_score = round(
                    0.25 * perf_score + 0.20 * specs_score + 0.20 * value_score + 0.15 * price_score + 0.10 * seller_trust + 0.10 * (100.0 - risk_score),
                    1,
                )
            elif "GAMING" in purpose_upper:
                overall_score = round(
                    0.30 * perf_score + 0.25 * specs_score + 0.15 * value_score + 0.15 * price_score + 0.10 * seller_trust + 0.05 * (100.0 - risk_score),
                    1,
                )
            else:  # GENERAL / BEST_OVERALL
                overall_score = round(
                    0.25 * perf_score + 0.20 * value_score + 0.20 * specs_score + 0.15 * price_score + 0.10 * seller_trust + 0.10 * (100.0 - risk_score),
                    1,
                )

            factor_score = ComparisonFactorScore(
                product_id=p.product_id,
                price_score=price_score,
                performance_score=perf_score,
                value_score=value_score,
                seller_trust_score=seller_trust,
                risk_score=risk_score,
                overall_score=overall_score,
            )
            scores_map[p.product_id] = factor_score

        # Sort Products Descending by Overall Score
        sorted_products = sorted(products, key=lambda p: scores_map[p.product_id].overall_score, reverse=True)

        # Assign Rank, Overall Score (out of 10.0), Why Ranked, Strengths, and Tradeoffs to Each Candidate
        for idx, prod in enumerate(sorted_products):
            rank_num = idx + 1
            sc = scores_map[prod.product_id]
            norm_score = round(sc.overall_score / 10.0, 1)

            prod.rank = rank_num
            prod.overall_score = norm_score

            why_list = []
            strengths_list = []
            tradeoffs_list = []

            if rank_num == 1:
                why_list.append(f"Highest composite performance & value score ({sc.overall_score}/100) for {purpose_upper.lower()} intent.")
            elif sc.value_score >= 80.0:
                why_list.append(f"Top value choice offering high performance at ₹{float(prod.price):,.2f}.")
            else:
                why_list.append(f"Balanced category contender with solid specs and seller trust.")

            if prod.specifications.cpu:
                strengths_list.append(f"Processor: {prod.specifications.cpu}")
            if prod.specifications.ram:
                strengths_list.append(f"Memory: {prod.specifications.ram}")
            if prod.specifications.gpu and "integrated" not in prod.specifications.gpu.lower():
                strengths_list.append(f"Graphics: {prod.specifications.gpu}")
            if prod.seller.seller_reputation in ("VERIFIED_BRAND_STORE", "PLATINUM_SELLER"):
                strengths_list.append(f"Trusted Seller: {prod.seller.seller_name} ({prod.seller.seller_reputation})")

            # Tradeoffs derivation
            if float(prod.price) > float(sorted_products[0].price) and rank_num > 1:
                tradeoffs_list.append(f"Priced higher than rank #1 option.")
            if "8gb" in (prod.specifications.ram or "").lower():
                tradeoffs_list.append("8GB RAM may limit heavy multi-tasking compared to 16GB models.")
            if not tradeoffs_list:
                tradeoffs_list.append("Standard market weight and battery life for this class.")

            prod.why_ranked = why_list
            prod.strengths = strengths_list
            prod.tradeoffs = tradeoffs_list

        scores_list = [scores_map[p.product_id] for p in sorted_products]

        best_overall = sorted_products[0].product_id
        best_value = max(sorted_products, key=lambda p: scores_map[p.product_id].value_score).product_id
        best_perf = max(sorted_products, key=lambda p: scores_map[p.product_id].performance_score).product_id
        lowest_risk = min(sorted_products, key=lambda p: scores_map[p.product_id].risk_score).product_id

        top_p = sorted_products[0]
        top_sc = scores_map[top_p.product_id]
        summary = (
            f"Evaluated {len(sorted_products)} listings for {purpose_upper} intent. "
            f"'{top_p.product_name}' ranks #1 BEST OVERALL (Score: {top_p.overall_score}/10) "
            f"with {top_p.specifications.cpu or 'high performance'}, {top_p.specifications.ram or 'RAM'}, "
            f"and trusted seller '{top_p.seller.seller_name}'."
        )

        return ProductComparisonMatrix(
            products=sorted_products,
            scores=scores_list,
            best_overall_id=best_overall,
            best_value_id=best_value,
            best_performance_id=best_perf,
            lowest_risk_id=lowest_risk,
            comparison_summary=summary,
        )
