"""Behaviour Risk Score Service Integration (Phase 251)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.behaviour_risk import BehaviourRiskResult as UpstreamBehaviourRiskResult
from app.schemas.ml_risk import MLBehaviourRiskResult

logger = logging.getLogger("fraudguard.ml.risk.behaviour")


class BehaviourRiskScoreService:
    """Governed Behaviour Risk Scoring Service integrating AGENTGUARD upstream (Phase 251)."""

    def process_behaviour_signal(
        self,
        upstream_signal: UpstreamBehaviourRiskResult | dict[str, Any],
        transaction_id: str,
        prediction_timestamp: datetime,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
        fallback_cold_start_score: float = 50.0,
    ) -> MLBehaviourRiskResult:
        """Process and validate upstream AGENTGUARD behaviour signal into MLBehaviourRiskResult (Phase 251)."""  # noqa: E501
        logger.info("Processing behaviour risk signal for transaction %s", transaction_id)

        # Parse upstream signal properties
        if isinstance(upstream_signal, UpstreamBehaviourRiskResult):
            tenant_id = upstream_signal.tenant_id
            agent_id = upstream_signal.agent_id
            raw_score = float(upstream_signal.behaviour_risk_score)
            raw_conf = float(upstream_signal.confidence)
            sig_time = upstream_signal.evaluated_at
            is_cold = upstream_signal.severity == "COLD_START" or raw_conf == 0.0
        elif isinstance(upstream_signal, dict):
            tenant_id = uuid.UUID(str(upstream_signal["tenant_id"]))
            agent_id = uuid.UUID(str(upstream_signal["agent_id"]))
            raw_score = float(upstream_signal.get("behaviour_risk_score", 0.0))
            raw_conf = float(upstream_signal.get("confidence", 1.0))
            sig_time = upstream_signal.get("evaluated_at", datetime.now(UTC))
            if isinstance(sig_time, str):
                sig_time = datetime.fromisoformat(sig_time)
            is_cold = bool(upstream_signal.get("is_cold_start", False)) or raw_conf == 0.0
        else:
            raise ValueError("Unsupported upstream behaviour signal type.")

        # 1. Identity Isolation Validation
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {expected_tenant_id}, got {tenant_id}")

        if expected_agent_id and agent_id != expected_agent_id:
            raise ValueError(f"Agent mismatch! Expected {expected_agent_id}, got {agent_id}")

        # 2. Temporal Point-in-Time Safety Validation
        p_time = (
            prediction_timestamp.replace(tzinfo=UTC)
            if prediction_timestamp.tzinfo is None
            else prediction_timestamp
        )  # noqa: E501
        s_time = sig_time.replace(tzinfo=UTC) if sig_time.tzinfo is None else sig_time

        if s_time > p_time:
            raise ValueError(
                "Point-in-time violation: behaviour signal timestamp is in the future!"
            )  # noqa: E501

        # 3. Confidence & Score Numerical Bounds Validation
        if math.isnan(raw_conf) or math.isinf(raw_conf) or raw_conf < 0.0 or raw_conf > 1.0:
            raise ValueError(f"Invalid behaviour confidence value: {raw_conf}")

        if math.isnan(raw_score) or math.isinf(raw_score) or raw_score < 0.0 or raw_score > 100.0:
            raise ValueError(f"Invalid behaviour risk score value: {raw_score}")

        # 4. Cold-Start Handling
        if is_cold:
            final_score = float(fallback_cold_start_score)
            logger.info(
                "Agent %s in cold-start state. Using fallback score %.2f", agent_id, final_score
            )  # noqa: E501
        else:
            final_score = round(raw_score, 4)

        sig_id = uuid.uuid4()
        conf_val = round(raw_conf, 4)

        cfg_payload = {
            "source_scale": "[0,100]",
            "target_scale": "[0,100]",
            "transformation_version": "1.0.0",
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "behaviour_risk_score": final_score,
            "behaviour_confidence": conf_val,
            "is_cold_start": is_cold,
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return MLBehaviourRiskResult(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            behaviour_risk_score=final_score,
            behaviour_confidence=conf_val,
            is_cold_start=is_cold,
            source_scale="[0,100]",
            target_scale="[0,100]",
            transformation_version="1.0.0",
            signal_timestamp=s_time,
            prediction_timestamp=p_time,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
        )
