"""Merchant Risk Score Service (Phase 252)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.ml_risk import MerchantRiskResult

logger = logging.getLogger("fraudguard.ml.risk.merchant")


class MerchantRiskScoreService:
    """Governed Merchant Risk Score Intelligence Service (Phase 252)."""

    def process_merchant_signal(
        self,
        signal_data: dict[str, Any],
        transaction_id: str,
        prediction_timestamp: datetime,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
        fallback_new_merchant_score: float = 50.0,
    ) -> MerchantRiskResult:
        """Process and validate upstream AGENTGUARD merchant signal into MerchantRiskResult (Phase 252)."""  # noqa: E501
        logger.info("Processing merchant risk signal for transaction %s", transaction_id)

        tenant_id = uuid.UUID(str(signal_data["tenant_id"]))
        agent_id = uuid.UUID(str(signal_data["agent_id"])) if signal_data.get("agent_id") else None  # noqa: E501
        merchant_id = (
            str(signal_data.get("merchant_id")) if signal_data.get("merchant_id") else None
        )  # noqa: E501

        # 1. Tenant & Agent Isolation Validation
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {expected_tenant_id}, got {tenant_id}")

        if expected_agent_id and agent_id and agent_id != expected_agent_id:
            raise ValueError(f"Agent mismatch! Expected {expected_agent_id}, got {agent_id}")

        # 2. Point-in-Time Temporal Safety Validation
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
            raise ValueError("Point-in-time violation: merchant signal timestamp is in the future!")  # noqa: E501

        # 3. Numerical Bounds & Distinction
        raw_risk = float(signal_data.get("merchant_risk_score", 0.0))
        raw_fam = float(signal_data.get("merchant_familiarity_score", 1.0))
        raw_conf = float(signal_data.get("confidence", 1.0))
        is_new = bool(signal_data.get("is_new_merchant", False))
        is_cold = bool(signal_data.get("is_cold_start", False)) or is_new

        if math.isnan(raw_risk) or math.isinf(raw_risk) or raw_risk < 0.0 or raw_risk > 100.0:
            raise ValueError(f"Invalid merchant risk score value: {raw_risk}")

        if math.isnan(raw_fam) or math.isinf(raw_fam) or raw_fam < 0.0 or raw_fam > 1.0:
            raise ValueError(f"Invalid merchant familiarity score value: {raw_fam}")

        if math.isnan(raw_conf) or math.isinf(raw_conf) or raw_conf < 0.0 or raw_conf > 1.0:
            raise ValueError(f"Invalid merchant confidence value: {raw_conf}")

        # Cold-Start / New-Merchant Fallback Score (Missing history does NOT mean safe)
        if is_new or is_cold:
            final_risk = float(fallback_new_merchant_score) if raw_risk == 0.0 else raw_risk
        else:
            final_risk = raw_risk

        final_risk = round(final_risk, 4)
        final_fam = round(raw_fam, 4)
        final_conf = round(raw_conf, 4)
        sig_id = uuid.uuid4()

        cfg_payload = {
            "version": "1.0.0",
            "source": "AGENTGUARD_MERCHANT_ANALYSIS",
            "fallback_score": fallback_new_merchant_score,
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        src_payload = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id) if agent_id else None,
            "merchant_id": merchant_id,
            "signal_timestamp": s_time.isoformat(),
        }
        src_hash = hashlib.sha256(json.dumps(src_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "merchant_risk_score": final_risk,
            "merchant_familiarity_score": final_fam,
            "confidence": final_conf,
            "is_new_merchant": is_new,
            "tenant_id": str(tenant_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return MerchantRiskResult(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            merchant_id=merchant_id,
            merchant_risk_score=final_risk,
            merchant_familiarity_score=final_fam,
            confidence=final_conf,
            is_new_merchant=is_new,
            is_cold_start=is_cold,
            source="AGENTGUARD_MERCHANT_ANALYSIS",
            signal_timestamp=s_time,
            prediction_timestamp=p_time,
            configuration_hash=cfg_hash,
            source_fingerprint=src_hash,
            result_fingerprint=res_hash,
        )
