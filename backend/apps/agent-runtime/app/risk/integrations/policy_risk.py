"""Policy Risk Integration Adapter (Phase 272)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)

logger = logging.getLogger("agentpay.risk.integrations.policy")

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


class PolicyRiskIntegrationService:
    """Production Policy Risk Integration Adapter (Phase 272)."""

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
        """Validate numeric float or Decimal against NaN and Infinity."""
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
        """Compute deterministic SHA-256 fingerprint for Policy risk signal."""
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

    def integrate_policy_risk(
        self,
        result: PolicyRiskResult | dict[str, Any],
        context: RiskEvaluationContext,
    ) -> list[RiskSignal]:
        """Convert authoritative Policy risk output into canonical RiskSignal objects (Phase 272)."""  # noqa: E501
        logger.info("Integrating Policy risk output into canonical RiskSignal pipeline")

        # 1. Extract raw identity attributes
        if isinstance(result, dict):
            t_id = result.get("tenant_id")
            a_id = result.get("agent_id")
            tx_id = result.get("transaction_id", context.transaction_id)
            raw_score = result.get("policy_risk_score")
            policy_dec = result.get("policy_decision")
            is_auth = bool(result.get("authoritative", True))
            allow_ml = bool(result.get("allow_ml_scoring", True))
            is_avail = bool(result.get("is_available", True))
            ts = result.get("signal_timestamp") or result.get(
                "evaluated_at", context.prediction_timestamp
            )
            src = str(result.get("source", "AGENTGUARD_POLICY_ENGINE"))
            src_ver = str(result.get("policy_version", getattr(result, "source_version", "1.0.0")))  # noqa: E501
            fp = str(result.get("result_fingerprint", ""))
            metadata = dict(result.get("metadata", {}))
        else:
            t_id = result.tenant_id
            a_id = result.agent_id
            tx_id = result.transaction_id
            raw_score = getattr(result, "policy_risk_score", None)
            policy_dec = getattr(result, "policy_decision", None)
            is_auth = getattr(result, "authoritative", True)
            allow_ml = getattr(result, "allow_ml_scoring", True)
            is_avail = getattr(result, "is_available", True)
            ts = getattr(result, "signal_timestamp", context.prediction_timestamp)
            src = getattr(result, "source", "AGENTGUARD_POLICY_ENGINE")
            src_ver = getattr(result, "policy_version", "1.0.0")
            fp = getattr(result, "result_fingerprint", "")
            metadata = {}

        # 2. Identity Binding Security Check
        if t_id and t_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! Policy tenant '{t_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if a_id and a_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! Policy agent '{a_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if tx_id and tx_id != context.transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! Policy tx '{tx_id}' != context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 3. Point-in-Time Timestamp Security Check
        if ts > context.prediction_timestamp:
            raise ValueError(
                f"Point-in-Time violation! Policy signal timestamp '{ts.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        # 4. Fail closed on UNKNOWN policy decision
        if policy_dec and str(policy_dec).upper() == "UNKNOWN":
            raise ValueError("Unrecognized or UNKNOWN policy decision encountered. Failing closed.")

        # Populate authoritative policy metadata
        if policy_dec:
            metadata["policy_decision"] = str(policy_dec)
            metadata["policy_authoritative"] = is_auth
            metadata["allow_ml_scoring"] = allow_ml
            metadata["policy_override_forbidden"] = True

        # Inspect metadata for target leakage
        self._inspect_target_leakage(metadata)

        signals: list[RiskSignal] = []

        # 5. Categorical Policy Decision Signal
        if policy_dec:
            if not fp:
                fp_dec = self._compute_fingerprint(
                    context.tenant_id,
                    context.agent_id,
                    context.transaction_id,
                    RiskSignalType.POLICY.value,
                    src,
                    ts,
                    None,
                    RiskScoreUnit.DECISION.value,
                    str(policy_dec),
                )
            else:
                fp_dec = fp

            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.POLICY,
                    source=src,
                    score=None,
                    score_unit=RiskScoreUnit.DECISION,
                    normalized_score=None,  # Invariant: Categorical policy decisions remain categorical!  # noqa: E501
                    decision=str(policy_dec),
                    timestamp=ts,
                    tenant_id=context.tenant_id,
                    agent_id=context.agent_id,
                    transaction_id=context.transaction_id,
                    source_version=src_ver,
                    source_fingerprint=fp_dec,
                    availability=is_avail,
                    metadata=metadata,
                )
            )

        # 6. Authoritative Numeric Policy Risk Score Signal (if present)
        score_val = self._validate_numeric(raw_score, "policy_risk_score")
        if score_val is not None:
            if score_val < 0.0 or score_val > 100.0:
                raise ValueError(f"Policy risk score {score_val} out of valid range [0.0, 100.0].")

            fp_score = self._compute_fingerprint(
                context.tenant_id,
                context.agent_id,
                context.transaction_id,
                RiskSignalType.POLICY.value,
                src,
                ts,
                score_val,
                RiskScoreUnit.RISK_SCORE.value,
                None,
            )

            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.POLICY,
                    source=src,
                    score=score_val,
                    score_unit=RiskScoreUnit.RISK_SCORE,
                    normalized_score=score_val,
                    timestamp=ts,
                    tenant_id=context.tenant_id,
                    agent_id=context.agent_id,
                    transaction_id=context.transaction_id,
                    source_version=src_ver,
                    source_fingerprint=fp_score,
                    availability=is_avail,
                    metadata=metadata,
                )
            )

        return signals
