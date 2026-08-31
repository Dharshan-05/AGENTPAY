"""ATIMConstraintEngine for constraint extraction and normalization."""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from app.schemas.atim import ATIMConstraint, ATIMProposedIntent

logger = logging.getLogger("agentpay.atim.constraints.engine")

ISO_CURRENCIES = {"USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "SGD"}


class ATIMConstraintEngine:
    """Production constraint engine for validating, normalizing, and verifying ATIM constraints."""

    def normalize_intent(self, raw_intent: ATIMProposedIntent) -> ATIMProposedIntent:
        """Normalize amount, currency, merchant, brand, constraints, and evaluate ambiguity."""
        # 1. Normalize currency
        normalized_currency = "USD"
        if raw_intent.currency:
            curr_upper = raw_intent.currency.strip().upper()
            if curr_upper in ISO_CURRENCIES or len(curr_upper) == 3:
                normalized_currency = curr_upper

        # 2. Normalize & validate financial amount
        normalized_amount = raw_intent.amount
        if normalized_amount is not None:
            try:
                dec_val = Decimal(str(normalized_amount)).quantize(Decimal("0.01"))
                if dec_val < Decimal("0.00"):
                    logger.warning("Negative financial amount %s reset to None", dec_val)
                    normalized_amount = None
                else:
                    normalized_amount = dec_val
            except (InvalidOperation, TypeError, ValueError):
                logger.warning("Invalid decimal amount %s reset to None", normalized_amount)
                normalized_amount = None

        # 3. Normalize merchant identifier
        normalized_merchant = None
        if raw_intent.merchant:
            clean_merch = raw_intent.merchant.strip().lower()
            normalized_merchant = re.sub(r"[^a-z0-9_\-]", "", clean_merch)

        # 4. Normalize category & brand & product
        normalized_category = raw_intent.category.strip().lower() if raw_intent.category else None
        normalized_brand = raw_intent.brand.strip().title() if raw_intent.brand else None
        normalized_product = raw_intent.product.strip() if raw_intent.product else None

        # 5. Normalize optimization
        normalized_opt = None
        if raw_intent.optimization:
            opt_str = raw_intent.optimization.strip().upper()
            if any(k in opt_str for k in ["CHEAPEST", "MIN_PRICE", "LOWEST_PRICE"]):
                normalized_opt = "MIN_PRICE"
            elif any(k in opt_str for k in ["BEST_RATED", "MAX_RATING", "HIGHEST_RATED"]):
                normalized_opt = "MAX_RATING"
            else:
                normalized_opt = opt_str

        # 6. Process & normalize constraints list
        normalized_constraints: list[ATIMConstraint] = []
        has_max_price_constraint = False
        for c in raw_intent.constraints:
            norm_c = self.normalize_single_constraint(c)
            if norm_c:
                normalized_constraints.append(norm_c)
                if norm_c.name in ("max_price", "budget", "amount_limit"):
                    has_max_price_constraint = True
                    if normalized_amount is None:
                        try:
                            normalized_amount = Decimal(str(norm_c.value)).quantize(Decimal("0.01"))
                        except Exception:
                            pass

        # 7. Deterministic Ambiguity & Completeness Assessment
        missing_fields: list[str] = []
        is_ambiguous = raw_intent.is_ambiguous
        ambiguity_reason = raw_intent.ambiguity_reason
        action = raw_intent.action.upper()

        if action in ("PAYMENT", "PRODUCT_SEARCH"):
            if normalized_amount is None and not has_max_price_constraint and action == "PAYMENT":
                missing_fields.append("amount")
            if not normalized_merchant and not normalized_product and not raw_intent.recipient and not raw_intent.target:
                missing_fields.append("merchant_or_product")

            if missing_fields:
                is_ambiguous = True
                ambiguity_reason = f"Missing mandatory fields: {', '.join(missing_fields)}"

        # If explicit vague request like "buy me something good"
        if raw_intent.target and any(w in raw_intent.target.lower() for w in ["something good", "the usual", "anything"]):
            is_ambiguous = True
            ambiguity_reason = "Vague purchase target"
            if "target" not in missing_fields:
                missing_fields.append("target")

        # Set confidence level deterministically
        if is_ambiguous:
            confidence_level = "AMBIGUOUS"
            calculated_confidence = min(raw_intent.confidence, Decimal("0.40"))
        elif action == "UNKNOWN":
            confidence_level = "INVALID"
            calculated_confidence = Decimal("0.00")
        elif raw_intent.confidence < Decimal("0.70"):
            confidence_level = "LOW_CONFIDENCE"
            calculated_confidence = raw_intent.confidence
        else:
            confidence_level = "HIGH_CONFIDENCE"
            calculated_confidence = raw_intent.confidence

        return raw_intent.model_copy(
            update={
                "currency": normalized_currency,
                "amount": normalized_amount,
                "merchant": normalized_merchant,
                "category": normalized_category,
                "brand": normalized_brand,
                "product": normalized_product,
                "optimization": normalized_opt,
                "constraints": normalized_constraints,
                "is_ambiguous": is_ambiguous,
                "ambiguity_reason": ambiguity_reason,
                "missing_fields": missing_fields,
                "confidence_level": confidence_level,
                "confidence": calculated_confidence,
            }
        )

    def normalize_single_constraint(self, constraint: ATIMConstraint) -> ATIMConstraint | None:
        """Validate and normalize an individual operational constraint."""
        c_name = constraint.name.strip().lower()
        if not c_name:
            return None

        val = constraint.value
        op = constraint.operator.strip().lower()

        # Specific normalization rules
        if c_name in ("max_price", "budget", "amount_limit", "under", "below"):
            try:
                val = float(Decimal(str(val)))
            except Exception:
                return None
            op = "lte"
            c_name = "max_price"
            is_sec = True
        elif c_name in ("min_rating", "rating", "stars"):
            try:
                val = min(5.0, max(0.0, float(val)))
            except Exception:
                return None
            op = "gte"
            c_name = "min_rating"
            is_sec = False
        elif c_name in ("brand", "make"):
            val = str(val).strip().title()
            op = "eq"
            c_name = "brand"
            is_sec = False
        elif c_name in ("quantity", "count"):
            try:
                val = max(1, int(val))
            except Exception:
                val = 1
            op = "eq"
            c_name = "quantity"
            is_sec = False
        else:
            is_sec = False

        return ATIMConstraint(
            name=c_name,
            operator=op,
            value=val,
            is_security_authoritative=is_sec or constraint.is_security_authoritative,
        )

