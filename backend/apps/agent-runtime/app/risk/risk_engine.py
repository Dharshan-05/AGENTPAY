"""Risk Engine Architecture Module (Phase 266)."""

from __future__ import annotations

import hashlib
import json
import logging

from app.risk.risk_config import compute_configuration_hash
from app.risk.signal_normalizer import RiskSignalNormalizer
from app.schemas.risk_engine import (
    RiskEngineConfig,
    RiskEngineResult,
    RiskEvaluationContext,
    RiskSignal,
)

logger = logging.getLogger("agentpay.risk.engine")


class RiskEngine:
    """Foundational Risk Engine Architecture (Phase 266)."""

    def __init__(
        self,
        config: RiskEngineConfig | None = None,
        normalizer: RiskSignalNormalizer | None = None,
    ) -> None:
        self.config = config or RiskEngineConfig()
        self.normalizer = normalizer or RiskSignalNormalizer()

    def evaluate(
        self,
        context: RiskEvaluationContext,
        signals: list[RiskSignal],
    ) -> RiskEngineResult:
        """Evaluate incoming risk signals within authoritative context (Phase 266)."""
        logger.info(
            "Executing RiskEngine evaluation %s for tx %s (tenant=%s, agent=%s)",
            context.evaluation_id,
            context.transaction_id,
            context.tenant_id,
            context.agent_id,
        )

        # 1. Authoritative Context Identity Check
        if not context.tenant_id or not context.agent_id or not context.transaction_id:
            raise ValueError("RiskEvaluationContext missing mandatory identity fields!")

        # 2. Normalize, Validate Identity, Check Timestamps, Deduplicate, Order Signals
        normalized_signals = self.normalizer.normalize_signals(signals, context=context)

        # 3. Source Fingerprints Extraction
        source_fingerprints = [s.source_fingerprint for s in normalized_signals]

        # 4. Engine Configuration Hash Calculation
        config_hash = compute_configuration_hash(self.config)

        # 5. Deterministic Result Fingerprint Calculation
        result_payload = {
            "evaluation_id": str(context.evaluation_id),
            "tenant_id": str(context.tenant_id),
            "agent_id": str(context.agent_id),
            "transaction_id": context.transaction_id,
            "prediction_timestamp": context.prediction_timestamp.isoformat(),
            "source_fingerprints": source_fingerprints,
            "configuration_hash": config_hash,
        }
        encoded = json.dumps(result_payload, sort_keys=True).encode("utf-8")
        result_fp = hashlib.sha256(encoded).hexdigest()

        return RiskEngineResult(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            normalized_signals=normalized_signals,
            source_fingerprints=source_fingerprints,
            configuration_hash=config_hash,
            result_fingerprint=result_fp,
        )
