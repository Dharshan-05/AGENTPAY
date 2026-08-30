"""Governed Risk Weight Configuration Service (Phase 275)."""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskSignalType,
    RiskWeightConfiguration,
)

logger = logging.getLogger("agentpay.risk.weights")

DEFAULT_GOVERNED_WEIGHTS: dict[str, Decimal] = {
    RiskSignalType.AGENTGUARD.value: Decimal("1.5"),
    RiskSignalType.FRAUDGUARD.value: Decimal("2.0"),
    RiskSignalType.BEHAVIOUR.value: Decimal("1.0"),
    RiskSignalType.INTENT.value: Decimal("1.0"),
    RiskSignalType.MERCHANT.value: Decimal("1.0"),
    RiskSignalType.VELOCITY.value: Decimal("1.0"),
    RiskSignalType.TRANSACTION.value: Decimal("1.5"),
}


class RiskWeightService:
    """Production Governed Risk Weight Configuration Service (Phase 275)."""

    def __init__(
        self,
        default_config: RiskWeightConfiguration | None = None,
    ) -> None:
        if default_config is None:
            default_config = RiskWeightConfiguration(
                configuration_version="1.0.0",
                weights=DEFAULT_GOVERNED_WEIGHTS,
                effective_from=datetime(2020, 1, 1, tzinfo=UTC),
                description="Default Production Governed Risk Weights",
            )
        self.validate_configuration(default_config)
        self.default_config = default_config

    def validate_configuration(
        self,
        config: RiskWeightConfiguration,
        context: RiskEvaluationContext | None = None,
    ) -> None:
        """Strictly validate governed RiskWeightConfiguration against architectural rules (Phase 275)."""  # noqa: E501
        if not config.weights:
            raise ValueError("Risk weight configuration cannot be empty.")

        # 1. Absolute Rule: POLICY must NOT be in ordinary advisory weights
        if RiskSignalType.POLICY.value in config.weights:
            raise ValueError(
                "POLICY signal cannot be assigned an advisory weight. Policy is an authoritative control plane."  # noqa: E501
            )

        valid_signal_types = {st.value for st in RiskSignalType}
        total_weight = Decimal("0.0")

        for sig_type_key, weight in config.weights.items():
            if sig_type_key not in valid_signal_types:
                raise ValueError(f"Unknown signal type '{sig_type_key}' in weight configuration.")

            if not isinstance(weight, Decimal):
                try:
                    weight_dec = Decimal(str(weight))
                except Exception as e:
                    raise ValueError(
                        f"Non-numeric weight value for signal type '{sig_type_key}': {e}"
                    ) from e
            else:
                weight_dec = weight

            if weight_dec.is_nan() or weight_dec.is_infinite():
                raise ValueError(
                    f"NaN or Infinity weight value detected for signal type '{sig_type_key}'."
                )

            val_float = float(weight_dec)
            if math.isnan(val_float) or math.isinf(val_float):
                raise ValueError(
                    f"NaN or Infinity weight value detected for signal type '{sig_type_key}'."
                )

            if weight_dec <= Decimal("0.0"):
                raise ValueError(
                    f"Weight for signal type '{sig_type_key}' must be strictly positive (> 0.0). Got {weight_dec}."  # noqa: E501
                )

            total_weight += weight_dec

        if total_weight <= Decimal("0.0"):
            raise ValueError("Total weight configuration sum must be strictly positive (> 0.0).")

        # 2. Context Isolation & Temporal Security Checks (if context is provided)
        if context is not None:
            if config.tenant_id and config.tenant_id != context.tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch in weight config! Config tenant '{config.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                )
            if config.agent_id and config.agent_id != context.agent_id:
                raise ValueError(
                    f"Agent ID mismatch in weight config! Config agent '{config.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                )
            if config.effective_from > context.prediction_timestamp:
                raise ValueError(
                    f"Weight config effective_from '{config.effective_from.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                )
            if config.effective_until and context.prediction_timestamp >= config.effective_until:
                raise ValueError(
                    f"Weight config effective_until '{config.effective_until.isoformat()}' expired relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                )

    def get_weight_configuration(
        self,
        context: RiskEvaluationContext,
        override_config: RiskWeightConfiguration | None = None,
    ) -> RiskWeightConfiguration:
        """Retrieve and validate governed RiskWeightConfiguration for evaluation context."""
        config = override_config or self.default_config
        self.validate_configuration(config, context=context)
        return config
