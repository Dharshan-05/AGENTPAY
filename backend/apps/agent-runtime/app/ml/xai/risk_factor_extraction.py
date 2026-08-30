"""Risk Factor Extraction Service (Phase 260)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime

from app.schemas.ml_risk import (
    MerchantRiskResult,
    MLBehaviourRiskResult,
    PolicyRiskResult,
    VelocityRiskResult,
)
from app.schemas.ml_xai import (
    LocalTransactionExplanation,
    RiskFactor,
    RiskFactorConfig,
    RiskFactorExtractionResult,
)

logger = logging.getLogger("fraudguard.ml.xai.extraction")


class RiskFactorExtractionService:
    """Production Risk Factor Extraction Service (Phase 260)."""

    def __init__(self, config: RiskFactorConfig | None = None) -> None:
        self.config = config or RiskFactorConfig()

    def _determine_severity(self, score: float) -> str:
        """Derive severity deterministically from risk score [0, 100]."""
        if score >= self.config.critical_threshold:
            return "CRITICAL"
        elif score >= self.config.high_threshold:
            return "HIGH"
        elif score >= self.config.medium_threshold:
            return "MEDIUM"
        else:
            return "LOW"

    def extract_risk_factors(
        self,
        tenant_id: uuid.UUID,
        transaction_id: str,
        local_explanation: LocalTransactionExplanation,
        policy_result: PolicyRiskResult | None = None,
        behaviour_result: MLBehaviourRiskResult | None = None,
        merchant_result: MerchantRiskResult | None = None,
        velocity_result: VelocityRiskResult | None = None,
        agent_id: uuid.UUID | None = None,
    ) -> RiskFactorExtractionResult:
        """Extract structured explainable risk factors from SHAP and risk signals (Phase 260)."""
        logger.info(
            "Extracting risk factors for transaction %s (tenant=%s)", transaction_id, tenant_id
        )

        if local_explanation.tenant_id != tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {tenant_id}")

        factors: list[RiskFactor] = []
        has_deny = False
        now = datetime.now(UTC)
        m_ver = local_explanation.model_version

        # 1. Authoritative Policy Risk Factor Extraction
        if policy_result:
            if policy_result.tenant_id != tenant_id:
                raise ValueError("Tenant mismatch in policy result.")
            if policy_result.policy_decision == "DENY":
                has_deny = True
                factors.append(
                    RiskFactor(
                        factor_type="POLICY",
                        feature_name="policy_decision",
                        source="AGENTGUARD_POLICY_ENGINE",
                        value=100.0,
                        unit="[0,100]",
                        direction="POSITIVE",
                        severity="CRITICAL",
                        description=f"Authoritative Policy DENY decision ({policy_result.policy_decision_code}).",  # noqa: E501
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        transaction_id=transaction_id,
                        model_version=m_ver,
                        created_at=now,
                    )
                )

        # 2. SHAP Model Feature Risk Factors Extraction
        for item in local_explanation.top_positive_factors:
            # Map SHAP positive magnitude to severity scale
            sev_score = min(100.0, abs(item.shap_value) * 100.0)
            sev = self._determine_severity(sev_score)
            factors.append(
                RiskFactor(
                    factor_type="MODEL_FEATURE",
                    feature_name=item.feature_name,
                    feature_version=item.feature_version,
                    source="FRAUDGUARD_XGBOOST_MODEL",
                    value=item.shap_value,
                    unit="SHAP_ATTRIBUTION",
                    direction="POSITIVE",
                    severity=sev,
                    shap_value=item.shap_value,
                    relative_importance=item.relative_importance,
                    description=f"Feature '{item.feature_name}' contributed positively (+{item.shap_value:.4f}) to fraud risk prediction.",  # noqa: E501
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    transaction_id=transaction_id,
                    model_version=m_ver,
                    created_at=now,
                )
            )

        # 3. Behaviour Risk Factor Extraction
        if behaviour_result:
            if behaviour_result.tenant_id != tenant_id:
                raise ValueError("Tenant mismatch in behaviour result.")
            sev = self._determine_severity(behaviour_result.behaviour_risk_score)
            factors.append(
                RiskFactor(
                    factor_type="BEHAVIOUR",
                    feature_name="behaviour_risk_score",
                    source="AGENTGUARD_BEHAVIOUR_ENGINE",
                    value=behaviour_result.behaviour_risk_score,
                    unit="[0,100]",
                    direction="POSITIVE"
                    if behaviour_result.behaviour_risk_score >= 50.0
                    else "NEUTRAL",  # noqa: E501
                    severity=sev,
                    description=f"Behaviour deviation risk score {behaviour_result.behaviour_risk_score:.2f} (confidence: {behaviour_result.behaviour_confidence:.2f}).",  # noqa: E501
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    transaction_id=transaction_id,
                    model_version=m_ver,
                    created_at=now,
                )
            )

        # 4. Merchant Risk Factor Extraction
        if merchant_result:
            if merchant_result.tenant_id != tenant_id:
                raise ValueError("Tenant mismatch in merchant result.")
            sev = self._determine_severity(merchant_result.merchant_risk_score)
            factors.append(
                RiskFactor(
                    factor_type="MERCHANT",
                    feature_name="merchant_risk_score",
                    source="AGENTGUARD_MERCHANT_ANALYSIS",
                    value=merchant_result.merchant_risk_score,
                    unit="[0,100]",
                    direction="POSITIVE"
                    if merchant_result.merchant_risk_score >= 50.0
                    else "NEUTRAL",  # noqa: E501
                    severity=sev,
                    description=f"Merchant risk score {merchant_result.merchant_risk_score:.2f} (new_merchant: {merchant_result.is_new_merchant}).",  # noqa: E501
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    transaction_id=transaction_id,
                    model_version=m_ver,
                    created_at=now,
                )
            )

        # 5. Velocity Risk Factor Extraction
        if velocity_result:
            if velocity_result.tenant_id != tenant_id:
                raise ValueError("Tenant mismatch in velocity result.")
            sev = self._determine_severity(velocity_result.velocity_risk_score)
            factors.append(
                RiskFactor(
                    factor_type="VELOCITY",
                    feature_name="velocity_risk_score",
                    source="AGENTGUARD_VELOCITY_ENGINE",
                    value=velocity_result.velocity_risk_score,
                    unit="[0,100]",
                    direction="POSITIVE"
                    if velocity_result.velocity_risk_score >= 50.0
                    else "NEUTRAL",  # noqa: E501
                    severity=sev,
                    description=f"Velocity risk score {velocity_result.velocity_risk_score:.2f} (burst_detected: {velocity_result.burst_detected}, window: {velocity_result.time_window}).",  # noqa: E501
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    transaction_id=transaction_id,
                    model_version=m_ver,
                    created_at=now,
                )
            )

        # Canonical factor deduplication by (factor_type, feature_name)
        seen_keys: set[tuple[str, str]] = set()
        dedup_factors: list[RiskFactor] = []
        for f in factors:
            key = (f.factor_type, f.feature_name or "")
            if key not in seen_keys:
                seen_keys.add(key)
                dedup_factors.append(f)

        ext_id = uuid.uuid4()

        cfg_payload = {"config_version": self.config.config_version, "version": "1.0.0"}
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "transaction_id": transaction_id,
            "tenant_id": str(tenant_id),
            "factor_count": len(dedup_factors),
            "has_deny": has_deny,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return RiskFactorExtractionResult(
            extraction_id=ext_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            factors=dedup_factors,
            has_policy_deny=has_deny,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
            created_at=now,
        )
