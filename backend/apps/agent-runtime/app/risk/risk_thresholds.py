"""Governed Risk Threshold Configuration & Evaluation Service (Phase 276)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskThresholdBand,
    RiskThresholdConfiguration,
    RiskThresholdEvaluationResult,
)

logger = logging.getLogger("agentpay.risk.thresholds")


class RiskThresholdService:
    """Production Governed Risk Threshold Configuration & Evaluation Service (Phase 276)."""

    def __init__(
        self,
        default_config: RiskThresholdConfiguration | None = None,
    ) -> None:
        if default_config is None:
            default_config = RiskThresholdConfiguration(
                configuration_version="1.0.0",
                allow_upper_bound=Decimal("30.0"),
                review_upper_bound=Decimal("70.0"),
                effective_from=datetime(2020, 1, 1, tzinfo=UTC),
                description="Default Production Governed Risk Thresholds",
            )
        self.validate_configuration(default_config)
        self.default_config = default_config

    def validate_configuration(
        self,
        config: RiskThresholdConfiguration,
        context: RiskEvaluationContext | None = None,
    ) -> None:
        """Strictly validate governed RiskThresholdConfiguration against architectural rules (Phase 276)."""  # noqa: E501
        allow_bound = config.allow_upper_bound
        review_bound = config.review_upper_bound

        # 1. Decimal & Numeric Safety Validation
        for name, val in [("allow_upper_bound", allow_bound), ("review_upper_bound", review_bound)]:
            if not isinstance(val, Decimal):
                try:
                    val_dec = Decimal(str(val))
                except Exception as e:
                    raise ValueError(f"Non-numeric threshold value for '{name}': {e}") from e
            else:
                val_dec = val

            if val_dec.is_nan() or val_dec.is_infinite():
                raise ValueError(f"NaN or Infinity threshold value detected for '{name}'.")

            val_float = float(val_dec)
            if math.isnan(val_float) or math.isinf(val_float):
                raise ValueError(f"NaN or Infinity threshold value detected for '{name}'.")

            if val_dec < Decimal("0.0") or val_dec > Decimal("100.0"):
                raise ValueError(f"Threshold '{name}' {val_dec} out of valid range [0.0, 100.0].")

        if allow_bound > review_bound:
            raise ValueError(
                f"Inverted threshold bounds detected! allow_upper_bound ({allow_bound}) > review_upper_bound ({review_bound})."  # noqa: E501
            )

        # 2. Context Isolation & Temporal Security Checks (if context provided)
        if context is not None:
            if config.tenant_id and config.tenant_id != context.tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch in threshold config! Config tenant '{config.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                )
            if config.agent_id and config.agent_id != context.agent_id:
                raise ValueError(
                    f"Agent ID mismatch in threshold config! Config agent '{config.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                )
            if config.effective_from > context.prediction_timestamp:
                raise ValueError(
                    f"Threshold config effective_from '{config.effective_from.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                )
            if config.effective_until and context.prediction_timestamp >= config.effective_until:
                raise ValueError(
                    f"Threshold config effective_until '{config.effective_until.isoformat()}' expired relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                )

    def evaluate_thresholds(
        self,
        calc_result: RiskScoreCalculationResult | float | Decimal,
        context: RiskEvaluationContext,
        override_config: RiskThresholdConfiguration | None = None,
    ) -> RiskThresholdEvaluationResult:
        """Evaluate non-authoritative risk threshold classification (Phase 276)."""
        config = override_config or self.default_config
        self.validate_configuration(config, context=context)
        config_hash = config.compute_hash()

        # 1. Extract and validate composite risk score
        if isinstance(calc_result, RiskScoreCalculationResult):
            # Identity Defense-in-Depth Validation
            if calc_result.tenant_id != context.tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch! Calc tenant '{calc_result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                )
            if calc_result.agent_id != context.agent_id:
                raise ValueError(
                    f"Agent ID mismatch! Calc agent '{calc_result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                )
            if calc_result.transaction_id != context.transaction_id:
                raise ValueError(
                    f"Transaction ID mismatch! Calc tx '{calc_result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
                )

            score_dec = calc_result.composite_risk_score_decimal
        elif isinstance(calc_result, Decimal):
            score_dec = calc_result
        else:
            score_dec = Decimal(str(calc_result))

        val_float = float(score_dec)
        if (
            math.isnan(val_float)
            or math.isinf(val_float)
            or score_dec.is_nan()
            or score_dec.is_infinite()
        ):  # noqa: E501
            raise ValueError("NaN or Infinity score value provided for threshold evaluation.")
        if score_dec < Decimal("0.0") or score_dec > Decimal("100.0"):
            raise ValueError(f"Score value {score_dec} out of valid range [0.0, 100.0].")

        score_float = float(score_dec)

        # 2. Threshold Classification Logic (Non-authoritative bands!)
        if score_dec <= config.allow_upper_bound:
            classification = "LOW"
            matched_band = RiskThresholdBand.LOW_RISK_BAND
        elif score_dec <= config.review_upper_bound:
            classification = "REVIEW_BAND"
            matched_band = RiskThresholdBand.MEDIUM_RISK_BAND
        else:
            classification = "HIGH"
            matched_band = RiskThresholdBand.HIGH_RISK_BAND

        # 3. Compute Deterministic Evaluation Fingerprint
        payload = {
            "evaluation_id": str(context.evaluation_id),
            "tenant_id": str(context.tenant_id),
            "agent_id": str(context.agent_id),
            "transaction_id": context.transaction_id,
            "prediction_timestamp": context.prediction_timestamp.isoformat(),
            "risk_score": str(score_dec),
            "classification": classification,
            "matched_threshold_band": matched_band.value,
            "configuration_hash": config_hash,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        eval_fp = hashlib.sha256(encoded).hexdigest()

        return RiskThresholdEvaluationResult(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            risk_score=score_float,
            risk_score_decimal=score_dec,
            classification=classification,
            matched_threshold_band=matched_band,
            configuration_version=config.configuration_version,
            configuration_hash=config_hash,
            evaluation_fingerprint=eval_fp,
        )
