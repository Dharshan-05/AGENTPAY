"""Risk Fusion Engine Foundation (Phase 273)."""

from __future__ import annotations

import hashlib
import json
import logging

from app.risk.risk_config import compute_configuration_hash
from app.risk.signal_normalizer import RiskSignalNormalizer
from app.schemas.risk_engine import (
    RiskEngineConfig,
    RiskEvaluationContext,
    RiskFusionResult,
    RiskSignal,
    RiskSignalType,
)

logger = logging.getLogger("agentpay.risk.fusion")


class RiskFusionEngine:
    """Production-grade Risk Fusion Engine (Phase 273)."""

    def __init__(
        self,
        config: RiskEngineConfig | None = None,
        normalizer: RiskSignalNormalizer | None = None,
    ) -> None:
        self.config = config or RiskEngineConfig()
        self.normalizer = normalizer or RiskSignalNormalizer()
        self.configuration_hash = compute_configuration_hash(self.config)

    def _compute_result_fingerprint(
        self,
        context: RiskEvaluationContext,
        normalized_signals: list[RiskSignal],
        policy_precedence: str,
    ) -> str:
        """Compute byte-identical SHA-256 fingerprint for fused risk representation."""
        signal_payloads = [
            {
                "signal_id": str(s.signal_id),
                "signal_type": s.signal_type.value,
                "source": s.source,
                "score": s.score,
                "score_unit": s.score_unit.value,
                "normalized_score": s.normalized_score,
                "confidence": s.confidence,
                "decision": s.decision,
                "timestamp": s.timestamp.isoformat(),
                "source_version": s.source_version,
                "source_fingerprint": s.source_fingerprint,
                "availability": s.availability,
                "cold_start": s.cold_start,
            }
            for s in normalized_signals
        ]

        payload = {
            "evaluation_id": str(context.evaluation_id),
            "tenant_id": str(context.tenant_id),
            "agent_id": str(context.agent_id),
            "transaction_id": context.transaction_id,
            "prediction_timestamp": context.prediction_timestamp.isoformat(),
            "policy_precedence": policy_precedence,
            "configuration_hash": self.configuration_hash,
            "signals": signal_payloads,
        }

        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def fuse(
        self,
        context: RiskEvaluationContext,
        signals: list[RiskSignal],
    ) -> RiskFusionResult:
        """Combine canonical normalized risk signals into a deterministic fused representation (Phase 273)."""  # noqa: E501
        logger.info(
            "Fusing %d signals for evaluation %s (tx=%s, tenant=%s)",
            len(signals),
            context.evaluation_id,
            context.transaction_id,
            context.tenant_id,
        )

        # 1. Normalize signals through canonical Normalizer (enforces identity, point-in-time, units, duplicates, conflicts, leakage)  # noqa: E501
        normalized_signals = self.normalizer.normalize_signals(signals, context=context)

        # 2. Group signals by type
        signals_by_type: dict[str, list[RiskSignal]] = {st.value: [] for st in RiskSignalType}
        for sig in normalized_signals:
            signals_by_type[sig.signal_type.value].append(sig)

        available_types: list[str] = []
        unavailable_types: list[str] = []

        for st_val, sig_list in signals_by_type.items():
            if any(s.availability for s in sig_list):
                available_types.append(st_val)
            else:
                unavailable_types.append(st_val)

        # 3. Classify into Authoritative Policy Control Signals vs Advisory Risk Signals
        policy_signals = signals_by_type.get(RiskSignalType.POLICY.value, [])
        advisory_signals = [s for s in normalized_signals if s.signal_type != RiskSignalType.POLICY]

        # 4. Evaluate Policy Precedence and Check for Policy Decisions Conflicts
        policy_decisions: set[str] = set()
        for ps in policy_signals:
            if ps.decision:
                policy_decisions.add(ps.decision.upper())

        if "DENY" in policy_decisions and "ALLOW" in policy_decisions:
            raise ValueError(
                "Conflicting policy decisions detected in policy control plane! ALLOW and DENY co-exist."  # noqa: E501
            )

        if "DENY" in policy_decisions:
            policy_precedence = "DENY"
        elif "REQUIRE_APPROVAL" in policy_decisions or "REVIEW" in policy_decisions:
            policy_precedence = "REVIEW"
        elif "ALLOW" in policy_decisions:
            policy_precedence = "ALLOW"
        else:
            policy_precedence = "NONE"

        # 5. Extract Source Fingerprints
        source_fingerprints = [s.source_fingerprint for s in normalized_signals]

        # 6. Compute Deterministic Result Fingerprint
        result_fingerprint = self._compute_result_fingerprint(
            context=context,
            normalized_signals=normalized_signals,
            policy_precedence=policy_precedence,
        )

        return RiskFusionResult(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            signals=normalized_signals,
            signals_by_type=signals_by_type,
            available_signal_types=available_types,
            unavailable_signal_types=unavailable_types,
            policy_signals=policy_signals,
            advisory_signals=advisory_signals,
            policy_precedence=policy_precedence,
            source_fingerprints=source_fingerprints,
            configuration_hash=self.configuration_hash,
            result_fingerprint=result_fingerprint,
        )
