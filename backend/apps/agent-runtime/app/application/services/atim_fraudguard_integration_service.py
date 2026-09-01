"""ATIM FRAUDGUARD Integration Service for feature provenance classification and ML risk evaluation (Phase 6)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field

from app.application.services.fraudguard_service import FraudGuardApplicationService
from app.schemas.fraudguard_api import (
    FraudGuardEvaluateRequest,
    FraudGuardEvaluateResponse,
)

logger = logging.getLogger("agentpay.atim.integration.fraudguard")


class FraudFeature(BaseModel):
    """Fraud feature model with explicit provenance tracking."""

    name: str
    value: Any
    source: Literal[
        "USER-PROVIDED",
        "AGENT-PROVIDED",
        "DATABASE",
        "TRANSACTION",
        "DEVICE",
        "BEHAVIORAL",
        "MERCHANT",
        "SYSTEM",
    ]
    trusted: bool = False


class ATIMFraudDecision(BaseModel):
    """Authoritative fraud evaluation decision envelope produced by FraudGuard."""

    risk_score: Decimal
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    decision: Literal["ALLOW", "REVIEW", "BLOCK"]
    model_version: str
    explanation_available: bool = False
    correlation_id: str
    top_risk_factors: list[str] = Field(default_factory=list)
    raw_evaluation_response: FraudGuardEvaluateResponse | None = None


class ATIMFraudGuardIntegrationService:
    """Production gateway connecting ATIM proposals to authoritative FraudGuard ML inference engine."""

    def __init__(
        self,
        fraudguard_service: FraudGuardApplicationService | None = None,
    ) -> None:
        self.fraudguard_service = fraudguard_service or FraudGuardApplicationService()

    def classify_feature_provenance(self, features: list[dict[str, Any]]) -> list[FraudFeature]:
        """Classify feature provenance to ensure untrusted LLM outputs are flagged untrusted."""
        classified: list[FraudFeature] = []
        for f in features:
            name = f.get("name", "unknown")
            val = f.get("value")
            src = f.get("source", "AGENT-PROVIDED")
            trusted = src in ("DATABASE", "TRANSACTION", "BEHAVIORAL", "SYSTEM")

            classified.append(
                FraudFeature(
                    name=name,
                    value=val,
                    source=src,
                    trusted=trusted,
                )
            )
        return classified

    async def evaluate_fraud_risk(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        merchant_id: str | None = None,
        feature_names: list[str] | None = None,
        feature_values: list[float] | None = None,
        include_xai: bool = True,
    ) -> ATIMFraudDecision:
        """Evaluate proposal against FraudGuard ML risk models fail-closed."""
        f_names = feature_names or [
            "transaction_amount",
            "velocity_1h",
            "merchant_risk_score",
            "behavioral_anomaly_score",
        ]
        f_vals = feature_values or [float(amount), 1.0, 0.1, 0.05]

        # Ensure feature vector alignment
        if len(f_names) != len(f_vals):
            min_len = min(len(f_names), len(f_vals))
            f_names = f_names[:min_len]
            f_vals = f_vals[:min_len]

        from datetime import timezone, datetime
        eval_req = FraudGuardEvaluateRequest(
            agent_id=agent_id,
            transaction_id=transaction_id,
            model_name="fraudguard_xgboost_prod",
            prediction_timestamp=datetime.now(timezone.utc),
            feature_names=f_names,
            feature_values=f_vals,
            include_xai=include_xai,
            top_k=5,
        )

        try:
            eval_res = self.fraudguard_service.evaluate_transaction(tenant_id, eval_req)

            prob = float(eval_res.advisory_risk_intelligence.fraud_probability)
            risk_score = Decimal(str(round(prob * 100.0, 2)))

            # Risk level classification
            if risk_score >= Decimal("85.00"):
                risk_level = "CRITICAL"
                decision = "BLOCK"
            elif risk_score >= Decimal("65.00"):
                risk_level = "HIGH"
                decision = "BLOCK"
            elif risk_score >= Decimal("40.00"):
                risk_level = "MEDIUM"
                decision = "REVIEW"
            else:
                risk_level = "LOW"
                decision = "ALLOW"

            factors = []
            if eval_res.local_explanation and eval_res.local_explanation.top_positive_factors:
                factors = [f.feature_name for f in eval_res.local_explanation.top_positive_factors]

            logger.info(
                "FRAUDGUARD evaluation for tx %s (tenant=%s, agent=%s): RiskScore=%s, Decision=%s",
                transaction_id,
                tenant_id,
                agent_id,
                risk_score,
                decision,
            )

            return ATIMFraudDecision(
                risk_score=risk_score,
                risk_level=risk_level,
                decision=decision,
                model_version=eval_res.advisory_risk_intelligence.result_fingerprint[:8],
                explanation_available=eval_res.local_explanation is not None,
                correlation_id=str(eval_res.evaluation_id),
                top_risk_factors=factors,
                raw_evaluation_response=eval_res,
            )
        except Exception as exc:
            logger.error("FraudGuard evaluation error for tx %s: %s", transaction_id, exc)
            # Fail closed on FraudGuard system error
            return ATIMFraudDecision(
                risk_score=Decimal("100.00"),
                risk_level="CRITICAL",
                decision="BLOCK",
                model_version="error_fallback",
                explanation_available=False,
                correlation_id=str(uuid.uuid4()),
                top_risk_factors=["FRAUDGUARD_SERVICE_UNAVAILABLE"],
            )
