"""Intent Risk Score Service (Phase 254)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.ml_risk import IntentRiskResult

logger = logging.getLogger("fraudguard.ml.risk.intent")


class IntentRiskScoreService:
    """Governed Intent Risk Score Intelligence Service (Phase 254)."""

    def process_intent_signal(
        self,
        signal_data: dict[str, Any] | None,
        transaction_id: str,
        prediction_timestamp: datetime,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
        fallback_unavailable_score: float = 50.0,
    ) -> IntentRiskResult:
        """Process and validate upstream AGENTGUARD intent signal into IntentRiskResult (Phase 254)."""  # noqa: E501
        logger.info("Processing intent risk signal for transaction %s", transaction_id)
        p_time = (
            prediction_timestamp.replace(tzinfo=UTC)
            if prediction_timestamp.tzinfo is None
            else prediction_timestamp
        )  # noqa: E501
        sig_id = uuid.uuid4()

        # Handle missing or unavailable intent data
        if not signal_data or not signal_data.get("is_available", True):
            tenant_id = expected_tenant_id or uuid.uuid4()
            agent_id = expected_agent_id

            cfg_payload = {
                "version": "1.0.0",
                "source": "AGENTGUARD_INTENT_ENGINE",
                "available": False,
            }  # noqa: E501
            cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

            return IntentRiskResult(
                risk_signal_id=sig_id,
                tenant_id=tenant_id,
                agent_id=agent_id,
                transaction_id=transaction_id,
                intent_risk_score=float(fallback_unavailable_score),
                intent_confidence=0.0,
                intent_can_proceed=False,
                intent_decision="UNAVAILABLE",
                is_available=False,
                source="AGENTGUARD_INTENT_ENGINE",
                signal_timestamp=p_time,
                prediction_timestamp=p_time,
                configuration_hash=cfg_hash,
                source_fingerprint=hashlib.sha256(b"unavailable_source").hexdigest(),
                result_fingerprint=hashlib.sha256(b"unavailable_result").hexdigest(),
            )

        tenant_id = uuid.UUID(str(signal_data["tenant_id"]))
        agent_id = uuid.UUID(str(signal_data["agent_id"])) if signal_data.get("agent_id") else None  # noqa: E501

        # 1. Isolation Validation
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {expected_tenant_id}, got {tenant_id}")

        if expected_agent_id and agent_id and agent_id != expected_agent_id:
            raise ValueError(f"Agent mismatch! Expected {expected_agent_id}, got {agent_id}")

        # 2. Point-in-Time Safety
        raw_sig_time = signal_data.get("signal_timestamp", datetime.now(UTC))
        if isinstance(raw_sig_time, str):
            s_time = datetime.fromisoformat(raw_sig_time).replace(tzinfo=UTC)
        else:
            s_time = (
                raw_sig_time.replace(tzinfo=UTC) if raw_sig_time.tzinfo is None else raw_sig_time
            )  # noqa: E501

        if s_time > p_time:
            raise ValueError("Point-in-time violation: intent signal timestamp is in the future!")  # noqa: E501

        # 3. Score & Confidence Bounds Validation
        raw_score = float(signal_data.get("intent_risk_score", 0.0))
        raw_conf = float(signal_data.get("intent_confidence", 1.0))
        can_proceed = bool(signal_data.get("intent_can_proceed", True))
        decision = str(signal_data.get("intent_decision", "VERIFIED"))

        if math.isnan(raw_score) or math.isinf(raw_score) or raw_score < 0.0 or raw_score > 100.0:
            raise ValueError(f"Invalid intent risk score value: {raw_score}")

        if math.isnan(raw_conf) or math.isinf(raw_conf) or raw_conf < 0.0 or raw_conf > 1.0:
            raise ValueError(f"Invalid intent confidence value: {raw_conf}")

        final_score = round(raw_score, 4)
        final_conf = round(raw_conf, 4)

        cfg_payload = {"version": "1.0.0", "source": "AGENTGUARD_INTENT_ENGINE", "available": True}
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        src_payload = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id) if agent_id else None,
            "decision": decision,
            "can_proceed": can_proceed,
            "signal_timestamp": s_time.isoformat(),
        }
        src_hash = hashlib.sha256(json.dumps(src_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "intent_risk_score": final_score,
            "intent_confidence": final_conf,
            "intent_can_proceed": can_proceed,
            "tenant_id": str(tenant_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return IntentRiskResult(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            intent_risk_score=final_score,
            intent_confidence=final_conf,
            intent_can_proceed=can_proceed,
            intent_decision=decision,
            is_available=True,
            source="AGENTGUARD_INTENT_ENGINE",
            signal_timestamp=s_time,
            prediction_timestamp=p_time,
            configuration_hash=cfg_hash,
            source_fingerprint=src_hash,
            result_fingerprint=res_hash,
        )
