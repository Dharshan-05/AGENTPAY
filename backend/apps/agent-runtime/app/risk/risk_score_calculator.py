"""Deterministic Composite Advisory Risk Score Calculator (Phase 274)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.risk.risk_weights import RiskWeightService
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskFusionResult,
    RiskScoreCalculationResult,
    RiskScoreUnit,
    RiskSignalType,
    RiskWeightConfiguration,
)

logger = logging.getLogger("agentpay.risk.calculator")

PROHIBITED_TARGET_FIELDS: frozenset[str] = frozenset(
    {
        "is_fraud",
        "fraud_label",
        "post_outcome",
        "chargeback_result",
        "investigation_result",
        "future_outcome",
    }
)


class RiskScoreCalculator:
    """Production Deterministic Advisory Risk Score Calculator (Phase 274)."""

    def __init__(
        self,
        weight_service: RiskWeightService | None = None,
    ) -> None:
        self.weight_service = weight_service or RiskWeightService()

    def _inspect_target_leakage(self, metadata: dict[str, Any]) -> None:
        """Inspect metadata for prohibited data leakage fields."""
        if not metadata:
            return
        for k, v in metadata.items():
            k_lower = str(k).lower()
            if k_lower in PROHIBITED_TARGET_FIELDS:
                raise ValueError(f"Prohibited target leakage field '{k}' detected in metadata.")
            v_str = str(v).lower()
            for target_field in PROHIBITED_TARGET_FIELDS:
                if target_field in v_str:
                    raise ValueError(
                        f"Prohibited target leakage value '{v_str}' detected in metadata field '{k}'."  # noqa: E501
                    )

    def _validate_numeric_score(self, val: float | None, name: str) -> None:
        """Validate numeric score against NaN, Infinity, and invalid range."""
        if val is None:
            return
        val_float = float(val)
        if math.isnan(val_float) or math.isinf(val_float):
            raise ValueError(f"NaN or Infinity score value detected for '{name}'.")
        if val_float < 0.0 or val_float > 100.0:
            raise ValueError(
                f"Normalized score {val_float} out of valid range [0.0, 100.0] for '{name}'."
            )

    def _compute_calculation_fingerprint(
        self,
        context_eval_id: Any,
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        prediction_timestamp: datetime,
        composite_score_dec: Decimal,
        weight_config_hash: str,
        policy_precedence: str,
        source_fingerprints: list[str],
    ) -> str:
        """Compute byte-identical SHA-256 fingerprint for score calculation result."""
        payload = {
            "evaluation_id": str(context_eval_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "prediction_timestamp": prediction_timestamp.isoformat(),
            "composite_risk_score": str(composite_score_dec),
            "weight_configuration_hash": weight_config_hash,
            "policy_precedence": policy_precedence,
            "source_fingerprints": sorted(source_fingerprints),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def calculate_score(
        self,
        fusion_result: RiskFusionResult,
        context: RiskEvaluationContext | None = None,
        weight_config: RiskWeightConfiguration | None = None,
    ) -> RiskScoreCalculationResult:
        """Calculate composite advisory risk score from fused normalized risk signals (Phase 274)."""  # noqa: E501
        logger.info(
            "Calculating composite advisory risk score for evaluation %s (tx=%s, tenant=%s)",
            fusion_result.evaluation_id,
            fusion_result.transaction_id,
            fusion_result.tenant_id,
        )

        # 1. Identity & Temporal Defense-in-Depth Validation (if context provided)
        if context is not None:
            if fusion_result.tenant_id != context.tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch! Fusion tenant '{fusion_result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                )
            if fusion_result.agent_id != context.agent_id:
                raise ValueError(
                    f"Agent ID mismatch! Fusion agent '{fusion_result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                )
            if fusion_result.transaction_id != context.transaction_id:
                raise ValueError(
                    f"Transaction ID mismatch! Fusion tx '{fusion_result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
                )

        eval_context = context or RiskEvaluationContext(
            tenant_id=fusion_result.tenant_id,
            agent_id=fusion_result.agent_id,
            transaction_id=fusion_result.transaction_id,
            prediction_timestamp=fusion_result.prediction_timestamp,
            evaluation_id=fusion_result.evaluation_id,
        )

        # 2. Retrieve and validate governed weight configuration
        config = self.weight_service.get_weight_configuration(
            context=eval_context,
            override_config=weight_config,
        )
        weight_config_hash = config.compute_hash()

        # 3. Categorize signals for score aggregation
        included_types: set[str] = set()
        excluded_types: set[str] = set()
        available_types: set[str] = set()
        unavailable_types: set[str] = set()

        weighted_sum = Decimal("0.0")
        total_applied_weight = Decimal("0.0")
        applied_weights_dict: dict[str, float] = {}

        # Order signals deterministically: (signal_type, source, timestamp, source_fingerprint)
        sorted_signals = sorted(
            fusion_result.signals,
            key=lambda s: (
                s.signal_type.value,
                s.source,
                s.timestamp.isoformat(),
                s.source_fingerprint,
            ),
        )

        for sig in sorted_signals:
            st_val = sig.signal_type.value

            # Target leakage & numeric safety inspection
            self._inspect_target_leakage(sig.metadata)
            self._validate_numeric_score(sig.normalized_score, st_val)

            if sig.availability:
                available_types.add(st_val)
            else:
                unavailable_types.add(st_val)
                excluded_types.add(st_val)
                continue

            # POLICY signals are control plane signals and excluded from advisory mathematical score  # noqa: E501
            if sig.signal_type == RiskSignalType.POLICY:
                excluded_types.add(st_val)
                continue

            # CONFIDENCE and DECISION signals are non-numeric risk score units and excluded from score sum  # noqa: E501
            if sig.normalized_score is None:
                excluded_types.add(st_val)
                continue

            # Only participate if weight is defined in weight configuration
            if st_val in config.weights:
                weight_dec = config.weights[st_val]
                score_dec = Decimal(str(sig.normalized_score))

                weighted_sum += weight_dec * score_dec
                total_applied_weight += weight_dec
                applied_weights_dict[st_val] = float(weight_dec)
                included_types.add(st_val)
            else:
                excluded_types.add(st_val)

        if total_applied_weight <= Decimal("0.0"):
            raise ValueError(
                "No valid available weighted risk signals found to compute composite score."
            )

        # 4. Financial-Grade Composite Advisory Risk Score Calculation
        composite_score_dec = weighted_sum / total_applied_weight
        composite_score_dec = max(Decimal("0.0"), min(Decimal("100.0"), composite_score_dec))
        composite_score_float = float(composite_score_dec)

        # 5. Deterministic Calculation Fingerprint
        calc_fp = self._compute_calculation_fingerprint(
            context_eval_id=eval_context.evaluation_id,
            tenant_id=eval_context.tenant_id,
            agent_id=eval_context.agent_id,
            transaction_id=eval_context.transaction_id,
            prediction_timestamp=eval_context.prediction_timestamp,
            composite_score_dec=composite_score_dec,
            weight_config_hash=weight_config_hash,
            policy_precedence=fusion_result.policy_precedence,
            source_fingerprints=fusion_result.source_fingerprints,
        )

        return RiskScoreCalculationResult(
            evaluation_id=eval_context.evaluation_id,
            tenant_id=eval_context.tenant_id,
            agent_id=eval_context.agent_id,
            transaction_id=eval_context.transaction_id,
            prediction_timestamp=eval_context.prediction_timestamp,
            composite_risk_score=composite_score_float,
            composite_risk_score_decimal=composite_score_dec,
            score_unit=RiskScoreUnit.RISK_SCORE,
            included_signal_types=sorted(included_types),
            excluded_signal_types=sorted(excluded_types - included_types),
            available_signal_types=sorted(available_types),
            unavailable_signal_types=sorted(unavailable_types),
            applied_weights=applied_weights_dict,
            total_applied_weight=float(total_applied_weight),
            weight_configuration_version=config.configuration_version,
            weight_configuration_hash=weight_config_hash,
            source_fingerprints=fusion_result.source_fingerprints,
            policy_precedence=fusion_result.policy_precedence,
            policy_authoritative=True,
            calculation_fingerprint=calc_fp,
        )
