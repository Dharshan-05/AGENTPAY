"""AGENTGUARD Risk Integration Adapter (Phase 268)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.schemas.agent_risk_profile import AgentRiskProfile
from app.schemas.behaviour_risk import BehaviourRiskResult
from app.schemas.ml_risk import MLBehaviourRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)

logger = logging.getLogger("agentpay.risk.integrations.agentguard")

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


class AgentGuardRiskIntegrationService:
    """Production AGENTGUARD Risk Integration Adapter (Phase 268)."""

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

    def _validate_numeric(self, val: float | Decimal | None, name: str) -> float | None:
        """Validate numeric value against NaN and Infinity."""
        if val is None:
            return None
        if isinstance(val, Decimal):
            if val.is_nan():
                raise ValueError(f"NaN value detected for '{name}'.")
            if val.is_infinite():
                raise ValueError(f"Infinity value detected for '{name}'.")
            val_float = float(val)
        else:
            val_float = float(val)

        if math.isnan(val_float) or math.isinf(val_float):
            raise ValueError(f"NaN or Infinity value detected for '{name}'.")
        return val_float

    def _compute_fingerprint(
        self,
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        signal_type: str,
        source: str,
        timestamp: datetime,
        score: float | None,
        score_unit: str,
        decision: str | None,
    ) -> str:
        """Compute deterministic SHA-256 fingerprint for AGENTGUARD signal."""
        payload = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "signal_type": signal_type,
            "source": source,
            "timestamp": timestamp.isoformat(),
            "score": score,
            "score_unit": score_unit,
            "decision": decision,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def integrate_agent_risk_profile(
        self,
        profile: AgentRiskProfile,
        context: RiskEvaluationContext,
    ) -> list[RiskSignal]:
        """Convert authoritative AgentRiskProfile into canonical RiskSignal objects (Phase 268)."""  # noqa: E501
        logger.info(
            "Integrating AgentRiskProfile for agent %s (tenant=%s)",
            profile.agent_id,
            profile.tenant_id,
        )

        # 1. Identity Binding Security Check
        if profile.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! AGENTGUARD profile tenant '{profile.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if profile.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! AGENTGUARD profile agent '{profile.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )

        # 2. Point-in-Time Timestamp Security Check
        if profile.evaluated_at > context.prediction_timestamp:
            raise ValueError(
                f"AGENTGUARD profile timestamp '{profile.evaluated_at.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        signals: list[RiskSignal] = []

        # Convert Decimal risk score safely
        raw_score = self._validate_numeric(profile.risk_score, "risk_score")
        if raw_score is not None:
            if raw_score < 0.0 or raw_score > 100.0:
                # Check scale: 0..1 vs 0..100
                if raw_score > 1.0 and raw_score <= 100.0:
                    score_val = raw_score
                elif raw_score <= 1.0 and raw_score >= 0.0:
                    score_val = raw_score * 100.0
                else:
                    raise ValueError(f"AGENTGUARD risk score {raw_score} out of valid range.")
            else:
                score_val = raw_score if raw_score > 1.0 else raw_score * 100.0

            is_cold = profile.risk_level.upper() == "COLD_START"
            metadata = {
                "risk_level": profile.risk_level,
                "trust_score": float(profile.trust_score),
                "explainable_reasons": profile.explainable_reasons,
            }
            self._inspect_target_leakage(metadata)

            fp = self._compute_fingerprint(
                profile.tenant_id,
                profile.agent_id,
                context.transaction_id,
                RiskSignalType.AGENTGUARD.value,
                "AGENTGUARD",
                profile.evaluated_at,
                score_val,
                RiskScoreUnit.RISK_SCORE.value,
                None,
            )

            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.AGENTGUARD,
                    source="AGENTGUARD",
                    score=score_val,
                    score_unit=RiskScoreUnit.RISK_SCORE,
                    normalized_score=score_val,
                    timestamp=profile.evaluated_at,
                    tenant_id=profile.tenant_id,
                    agent_id=profile.agent_id,
                    transaction_id=context.transaction_id,
                    source_fingerprint=fp,
                    cold_start=is_cold,
                    metadata=metadata,
                )
            )

        # Categorical Decision Signal (Preserve as DECISION, NOT converted into numeric 0 or 100!)
        if profile.recommended_action:
            fp_dec = self._compute_fingerprint(
                profile.tenant_id,
                profile.agent_id,
                context.transaction_id,
                RiskSignalType.AGENTGUARD.value,
                "AGENTGUARD",
                profile.evaluated_at,
                None,
                RiskScoreUnit.DECISION.value,
                profile.recommended_action,
            )
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.AGENTGUARD,
                    source="AGENTGUARD",
                    score=None,
                    score_unit=RiskScoreUnit.DECISION,
                    normalized_score=None,  # Invariant: Decision signals remain categorical!
                    decision=profile.recommended_action,
                    timestamp=profile.evaluated_at,
                    tenant_id=profile.tenant_id,
                    agent_id=profile.agent_id,
                    transaction_id=context.transaction_id,
                    source_fingerprint=fp_dec,
                    cold_start=profile.risk_level.upper() == "COLD_START",
                )
            )

        return signals

    def integrate_behaviour_risk_result(
        self,
        result: BehaviourRiskResult | MLBehaviourRiskResult,
        context: RiskEvaluationContext,
    ) -> list[RiskSignal]:
        """Convert authoritative BehaviourRiskResult or MLBehaviourRiskResult into RiskSignal (Phase 268)."""  # noqa: E501
        logger.info(
            "Integrating BehaviourRiskResult for agent %s (tenant=%s)",
            result.agent_id,
            result.tenant_id,
        )

        # 1. Identity Binding Security Check
        if result.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! Behaviour result tenant '{result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if result.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! Behaviour result agent '{result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if hasattr(result, "transaction_id") and result.transaction_id:
            if result.transaction_id != context.transaction_id:
                raise ValueError(
                    f"Transaction ID mismatch! Behaviour result tx '{result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
                )

        # 2. Point-in-Time Timestamp Security Check
        ts = getattr(result, "evaluated_at", getattr(result, "signal_timestamp", None))
        if ts is None:
            ts = context.prediction_timestamp
        if ts > context.prediction_timestamp:
            raise ValueError(
                f"Behaviour signal timestamp '{ts.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        signals: list[RiskSignal] = []

        # Behaviour Risk Score
        raw_score = getattr(result, "behaviour_risk_score", None)
        score_val = self._validate_numeric(raw_score, "behaviour_risk_score")

        if score_val is not None:
            # 0..1 Decimal vs 0..100 float check
            if score_val <= 1.0 and score_val >= 0.0:
                normalized_score = score_val * 100.0
            elif score_val <= 100.0 and score_val >= 0.0:
                normalized_score = score_val
            else:
                raise ValueError(f"Behaviour risk score {score_val} out of valid range.")

            is_cold = getattr(result, "is_cold_start", False)
            if hasattr(result, "severity") and result.severity.upper() == "COLD_START":
                is_cold = True

            fp = getattr(result, "result_fingerprint", "")
            if not fp:
                fp = self._compute_fingerprint(
                    result.tenant_id,
                    result.agent_id,
                    context.transaction_id,
                    RiskSignalType.BEHAVIOUR.value,
                    "BEHAVIOUR",
                    ts,
                    normalized_score,
                    RiskScoreUnit.RISK_SCORE.value,
                    None,
                )

            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.BEHAVIOUR,
                    source="BEHAVIOUR",
                    score=normalized_score,
                    score_unit=RiskScoreUnit.RISK_SCORE,
                    normalized_score=normalized_score,
                    timestamp=ts,
                    tenant_id=result.tenant_id,
                    agent_id=result.agent_id,
                    transaction_id=context.transaction_id,
                    source_fingerprint=fp,
                    cold_start=is_cold,
                )
            )

        # Behaviour Confidence Signal (Preserved separately as CONFIDENCE, NEVER converted to risk score!)  # noqa: E501
        raw_conf = getattr(result, "confidence", getattr(result, "behaviour_confidence", None))
        conf_val = self._validate_numeric(raw_conf, "confidence")

        if conf_val is not None:
            if conf_val < 0.0 or conf_val > 1.0:
                raise ValueError(f"Behaviour confidence {conf_val} out of valid range [0.0, 1.0].")

            fp_conf = self._compute_fingerprint(
                result.tenant_id,
                result.agent_id,
                context.transaction_id,
                RiskSignalType.BEHAVIOUR.value,
                "BEHAVIOUR",
                ts,
                None,
                RiskScoreUnit.CONFIDENCE.value,
                None,
            )

            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.BEHAVIOUR,
                    source="BEHAVIOUR",
                    score=None,
                    score_unit=RiskScoreUnit.CONFIDENCE,
                    normalized_score=None,  # Invariant: Confidence is NEVER converted into risk score!  # noqa: E501
                    confidence=conf_val,
                    timestamp=ts,
                    tenant_id=result.tenant_id,
                    agent_id=result.agent_id,
                    transaction_id=context.transaction_id,
                    source_fingerprint=fp_conf,
                    cold_start=getattr(result, "is_cold_start", False),
                )
            )

        return signals
