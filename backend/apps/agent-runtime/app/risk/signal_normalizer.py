"""Risk Signal Normalizer Module (Phase 267)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from decimal import Decimal
from typing import Any

from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
)

logger = logging.getLogger("agentpay.risk.normalizer")

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


class RiskSignalNormalizer:
    """Deterministic Normalization Layer for Heterogeneous Risk Signals (Phase 267)."""

    def _inspect_target_leakage(self, metadata: dict[str, Any]) -> None:
        """Inspect metadata for prohibited data leakage fields (Phase 267)."""
        if not metadata:
            return

        for k, v in metadata.items():
            k_lower = str(k).lower()
            if k_lower in PROHIBITED_TARGET_FIELDS:
                raise ValueError(
                    f"Prohibited target leakage field '{k}' detected in signal metadata."
                )

            v_str = str(v).lower()
            for target_field in PROHIBITED_TARGET_FIELDS:
                if target_field in v_str:
                    raise ValueError(
                        f"Prohibited target leakage value '{v_str}' detected in signal metadata field '{k}'."  # noqa: E501
                    )

    def _validate_numeric_value(self, val: float | Decimal | None, field_name: str) -> float | None:
        """Validate numeric value against NaN and Infinity."""
        if val is None:
            return None
        if isinstance(val, Decimal):
            if val.is_nan():
                raise ValueError(f"NaN value detected for field '{field_name}'.")
            if val.is_infinite():
                raise ValueError(f"Infinity value detected for field '{field_name}'.")
            val_float = float(val)
        else:
            val_float = float(val)

        if math.isnan(val_float) or math.isinf(val_float):
            raise ValueError(f"NaN or Infinity value detected for field '{field_name}'.")
        return val_float

    def compute_signal_fingerprint(self, signal: RiskSignal) -> str:
        """Compute canonical SHA-256 fingerprint hash for RiskSignal."""
        payload = {
            "tenant_id": str(signal.tenant_id),
            "agent_id": str(signal.agent_id),
            "transaction_id": signal.transaction_id,
            "signal_type": signal.signal_type.value,
            "source": signal.source,
            "source_version": signal.source_version,
            "timestamp": signal.timestamp.isoformat(),
            "score": signal.score,
            "score_unit": signal.score_unit.value,
            "confidence": signal.confidence,
            "decision": signal.decision,
            "availability": signal.availability,
            "cold_start": signal.cold_start,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def normalize_signal(
        self,
        signal: RiskSignal,
        context: RiskEvaluationContext | None = None,
    ) -> RiskSignal:
        """Normalize an individual RiskSignal (Phase 267)."""
        # 1. Target Leakage Verification
        self._inspect_target_leakage(signal.metadata)

        # 2. Identity Binding Validation (if context provided)
        if context is not None:
            if not signal.tenant_id or signal.tenant_id != context.tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch! Signal tenant '{signal.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                )
            if not signal.agent_id or signal.agent_id != context.agent_id:
                raise ValueError(
                    f"Agent ID mismatch! Signal agent '{signal.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                )
            if not signal.transaction_id or signal.transaction_id != context.transaction_id:
                raise ValueError(
                    f"Transaction ID mismatch! Signal tx '{signal.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
                )

            # 3. Point-in-Time Timestamp Validation
            if signal.timestamp > context.prediction_timestamp:
                raise ValueError(
                    f"Signal timestamp '{signal.timestamp.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                )

        # 4. Numeric & Range Safety Validation
        raw_score = self._validate_numeric_value(signal.score, "score")
        conf_val = self._validate_numeric_value(signal.confidence, "confidence")

        normalized_score: float | None = None

        if signal.score_unit == RiskScoreUnit.PROBABILITY:
            if raw_score is None and signal.availability:
                raise ValueError("Probability signal missing numeric score.")
            if raw_score is not None:
                if raw_score < 0.0 or raw_score > 1.0:
                    raise ValueError(
                        f"Probability score {raw_score} out of valid range [0.0, 1.0]."
                    )
                normalized_score = raw_score * 100.0

        elif signal.score_unit == RiskScoreUnit.RISK_SCORE:
            if raw_score is None and signal.availability:
                raise ValueError("Risk score signal missing numeric score.")
            if raw_score is not None:
                if raw_score < 0.0 or raw_score > 100.0:
                    raise ValueError(f"Risk score {raw_score} out of valid range [0.0, 100.0].")
                normalized_score = raw_score

        elif signal.score_unit == RiskScoreUnit.CONFIDENCE:
            effective_conf = conf_val if conf_val is not None else raw_score
            if effective_conf is None and signal.availability:
                raise ValueError("Confidence signal missing numeric confidence value.")
            if effective_conf is not None:
                if effective_conf < 0.0 or effective_conf > 1.0:
                    raise ValueError(
                        f"Confidence score {effective_conf} out of valid range [0.0, 1.0]."
                    )
                conf_val = effective_conf
            # Mandatory Invariant: Confidence is NEVER converted into a normalized risk score!
            normalized_score = None

        elif signal.score_unit == RiskScoreUnit.DECISION:
            dec_str: str | None = None
            if signal.decision:
                dec_str = signal.decision
            elif raw_score is not None:
                dec_str = str(raw_score)

            if not dec_str and signal.availability:
                raise ValueError("Decision signal missing categorical decision value.")

            # Decision signals remain categorical and are NOT converted into numeric risk scores!
            normalized_score = None

        # 5. Unavailable & Cold Start Signals Integrity
        if not signal.availability:
            normalized_score = None

        # 6. Source Provenance Fingerprinting
        fp = signal.source_fingerprint
        if not fp:
            temp_signal = signal.model_copy(
                update={
                    "score": raw_score,
                    "confidence": conf_val,
                    "normalized_score": normalized_score,
                }  # noqa: E501
            )
            fp = self.compute_signal_fingerprint(temp_signal)

        return signal.model_copy(
            update={
                "score": raw_score,
                "confidence": conf_val,
                "normalized_score": normalized_score,
                "source_fingerprint": fp,
            }
        )

    def normalize_signals(
        self,
        signals: list[RiskSignal],
        context: RiskEvaluationContext | None = None,
    ) -> list[RiskSignal]:
        """Normalize, validate, deduplicate, and deterministically order signals (Phase 267)."""
        normalized_list: list[RiskSignal] = []

        # 1. Normalize individual signals
        for sig in signals:
            norm_sig = self.normalize_signal(sig, context=context)
            normalized_list.append(norm_sig)

        # 2. Duplicate Detection & Conflict Verification
        seen_signals: dict[tuple[Any, ...], RiskSignal] = {}

        for sig in normalized_list:
            dedup_key = (
                str(sig.tenant_id),
                str(sig.agent_id),
                sig.transaction_id,
                sig.signal_type.value,
                sig.source,
                sig.source_version,
                sig.score_unit.value,
                sig.timestamp.isoformat(),
            )

            if dedup_key in seen_signals:
                existing = seen_signals[dedup_key]
                # Compare critical signal payloads for conflict
                if (
                    existing.score != sig.score
                    or existing.score_unit != sig.score_unit
                    or existing.confidence != sig.confidence
                    or existing.decision != sig.decision
                    or existing.normalized_score != sig.normalized_score
                    or existing.availability != sig.availability
                    or existing.cold_start != sig.cold_start
                ):
                    raise ValueError(
                        f"Conflicting duplicate signal detected for source '{sig.source}' of type '{sig.signal_type.value}'!"  # noqa: E501
                    )
            else:
                seen_signals[dedup_key] = sig

        deduplicated_list = list(seen_signals.values())

        # 3. Deterministic Ordering
        # Order by: signal_type, source, timestamp, source_fingerprint
        deduplicated_list.sort(
            key=lambda s: (
                s.signal_type.value,
                s.source,
                s.timestamp.isoformat(),
                s.source_fingerprint,
            )
        )

        return deduplicated_list
