"""Velocity Risk Score Service (Phase 253)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.schemas.ml_risk import VelocityRiskResult

logger = logging.getLogger("fraudguard.ml.risk.velocity")


class VelocityRiskScoreService:
    """Governed Velocity Risk Score Intelligence Service (Phase 253)."""

    def process_velocity_signal(
        self,
        signal_data: dict[str, Any],
        transaction_id: str,
        prediction_timestamp: datetime,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
    ) -> VelocityRiskResult:
        """Process and validate upstream AGENTGUARD velocity signal into VelocityRiskResult (Phase 253)."""  # noqa: E501
        logger.info("Processing velocity risk signal for transaction %s", transaction_id)

        tenant_id = uuid.UUID(str(signal_data["tenant_id"]))
        agent_id = uuid.UUID(str(signal_data["agent_id"])) if signal_data.get("agent_id") else None  # noqa: E501

        # 1. Isolation Validation
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {expected_tenant_id}, got {tenant_id}")

        if expected_agent_id and agent_id and agent_id != expected_agent_id:
            raise ValueError(f"Agent mismatch! Expected {expected_agent_id}, got {agent_id}")

        # 2. Point-in-Time Temporal Safety
        p_time = (
            prediction_timestamp.replace(tzinfo=UTC)
            if prediction_timestamp.tzinfo is None
            else prediction_timestamp
        )  # noqa: E501
        raw_sig_time = signal_data.get("signal_timestamp", datetime.now(UTC))
        if isinstance(raw_sig_time, str):
            s_time = datetime.fromisoformat(raw_sig_time).replace(tzinfo=UTC)
        else:
            s_time = (
                raw_sig_time.replace(tzinfo=UTC) if raw_sig_time.tzinfo is None else raw_sig_time
            )  # noqa: E501

        if s_time > p_time:
            raise ValueError("Point-in-time violation: velocity signal timestamp is in the future!")  # noqa: E501

        # 3. Numerical Safety & Bounds Check
        raw_score = float(signal_data.get("velocity_risk_score", 0.0))
        raw_conf = float(signal_data.get("confidence", 1.0))
        burst = bool(signal_data.get("burst_detected", False))
        tx_count = int(signal_data.get("transaction_count", 0))
        raw_amt_vel = signal_data.get("amount_velocity", 0.0)

        # Decimal precision handling at boundary
        if isinstance(raw_amt_vel, Decimal):
            amt_vel = float(raw_amt_vel)
        else:
            amt_vel = float(raw_amt_vel)

        if math.isnan(raw_score) or math.isinf(raw_score) or raw_score < 0.0 or raw_score > 100.0:
            raise ValueError(f"Invalid velocity risk score value: {raw_score}")

        if math.isnan(raw_conf) or math.isinf(raw_conf) or raw_conf < 0.0 or raw_conf > 1.0:
            raise ValueError(f"Invalid velocity confidence value: {raw_conf}")

        if math.isnan(amt_vel) or math.isinf(amt_vel) or amt_vel < 0.0:
            raise ValueError(f"Invalid amount velocity value: {amt_vel}")

        time_win = str(signal_data.get("time_window", "1h"))
        final_score = round(raw_score, 4)
        final_conf = round(raw_conf, 4)
        amt_vel = round(amt_vel, 2)
        sig_id = uuid.uuid4()

        cfg_payload = {
            "version": "1.0.0",
            "source": "AGENTGUARD_VELOCITY_ENGINE",
            "window": time_win,
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        src_payload = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id) if agent_id else None,
            "tx_count": tx_count,
            "amt_vel": amt_vel,
            "signal_timestamp": s_time.isoformat(),
        }
        src_hash = hashlib.sha256(json.dumps(src_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "velocity_risk_score": final_score,
            "burst_detected": burst,
            "confidence": final_conf,
            "tenant_id": str(tenant_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return VelocityRiskResult(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            velocity_risk_score=final_score,
            burst_detected=burst,
            transaction_count=tx_count,
            amount_velocity=amt_vel,
            time_window=time_win,
            confidence=final_conf,
            source="AGENTGUARD_VELOCITY_ENGINE",
            signal_timestamp=s_time,
            prediction_timestamp=p_time,
            configuration_hash=cfg_hash,
            source_fingerprint=src_hash,
            result_fingerprint=res_hash,
        )
