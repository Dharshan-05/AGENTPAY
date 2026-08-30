"""FraudGuard Application Orchestration Service (Phases 261-265)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime

import numpy as np

from app.ml.inference.inference_engine import FraudGuardInferenceEngine
from app.ml.registry.model_registry import ModelRegistry
from app.ml.risk.behaviour_risk import BehaviourRiskScoreService
from app.ml.risk.fraud_probability import FraudProbabilityService
from app.ml.risk.intent_risk import IntentRiskScoreService
from app.ml.risk.merchant_risk import MerchantRiskScoreService
from app.ml.risk.policy_risk import PolicyRiskScoreService
from app.ml.risk.transaction_risk import TransactionRiskService
from app.ml.risk.velocity_risk import VelocityRiskScoreService
from app.ml.xai.feature_importance import ShapFeatureImportanceService
from app.ml.xai.global_explanation import GlobalModelExplanationService
from app.ml.xai.local_explanation import LocalTransactionExplanationService
from app.ml.xai.risk_factor_extraction import RiskFactorExtractionService
from app.ml.xai.shap_integration import ShapIntegrationService
from app.schemas.fraudguard_api import (
    FraudGuardEvaluateRequest,
    FraudGuardEvaluateResponse,
    FraudGuardGlobalXAIRequest,
    FraudGuardInferenceRequest,
    FraudGuardInferenceResponse,
    FraudGuardLocalXAIRequest,
    FraudGuardRiskIntelligenceRequest,
    FraudGuardRiskIntelligenceResponse,
)
from app.schemas.ml_inference import InferenceRequest
from app.schemas.ml_xai import GlobalModelExplanation, LocalTransactionExplanation

logger = logging.getLogger("fraudguard.application.service")


class FraudGuardApplicationService:
    """Production Orchestration Service for FraudGuard Inference, Risk & XAI (Phases 261-265)."""  # noqa: E501

    def __init__(
        self,
        registry: ModelRegistry | None = None,
        inference_engine: FraudGuardInferenceEngine | None = None,
        probability_service: FraudProbabilityService | None = None,
        transaction_risk_service: TransactionRiskService | None = None,
        behaviour_risk_service: BehaviourRiskScoreService | None = None,
        merchant_risk_service: MerchantRiskScoreService | None = None,
        velocity_risk_service: VelocityRiskScoreService | None = None,
        intent_risk_service: IntentRiskScoreService | None = None,
        policy_risk_service: PolicyRiskScoreService | None = None,
        shap_service: ShapIntegrationService | None = None,
        importance_service: ShapFeatureImportanceService | None = None,
        local_xai_service: LocalTransactionExplanationService | None = None,
        global_xai_service: GlobalModelExplanationService | None = None,
        extraction_service: RiskFactorExtractionService | None = None,
    ) -> None:
        self.registry = registry or ModelRegistry()
        self.inference_engine = inference_engine or FraudGuardInferenceEngine(
            registry=self.registry
        )
        self.probability_service = probability_service or FraudProbabilityService()
        self.transaction_risk_service = transaction_risk_service or TransactionRiskService()
        self.behaviour_risk_service = behaviour_risk_service or BehaviourRiskScoreService()
        self.merchant_risk_service = merchant_risk_service or MerchantRiskScoreService()
        self.velocity_risk_service = velocity_risk_service or VelocityRiskScoreService()
        self.intent_risk_service = intent_risk_service or IntentRiskScoreService()
        self.policy_risk_service = policy_risk_service or PolicyRiskScoreService()
        self.shap_service = shap_service or ShapIntegrationService(registry=self.registry)
        self.importance_service = importance_service or ShapFeatureImportanceService()
        self.local_xai_service = local_xai_service or LocalTransactionExplanationService(
            importance_service=self.importance_service
        )
        self.global_xai_service = global_xai_service or GlobalModelExplanationService(
            registry=self.registry
        )
        self.extraction_service = extraction_service or RiskFactorExtractionService()

    # -----------------------------------------------------------------------
    # Phase 263: Real-Time Inference API Service
    # -----------------------------------------------------------------------
    def run_inference(
        self,
        tenant_id: uuid.UUID,
        request: FraudGuardInferenceRequest,
    ) -> FraudGuardInferenceResponse:
        """Orchestrate real-time FraudGuard inference (Phase 263)."""
        logger.info(
            "Executing FraudGuard API inference for tx %s (tenant=%s)",
            request.transaction_id,
            tenant_id,
        )

        feat_dict = dict(zip(request.feature_names, request.feature_values, strict=True))
        inf_req = InferenceRequest(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_name=request.model_name,
            prediction_timestamp=request.prediction_timestamp,
            feature_values=feat_dict,
            feature_timestamps=request.feature_timestamps or {},
            required_feature_versions=request.feature_versions or {},
        )

        inf_res, _ = self.inference_engine.predict_fraud(inf_req)

        reg_manifest = (
            self.registry.get_model(tenant_id, request.model_name, request.model_version)
            if request.model_version
            else self.registry.resolve_production_model(tenant_id, request.model_name)
        )

        res_hash = hashlib.sha256(
            json.dumps(
                {"inf_id": str(inf_res.inference_id), "prob": inf_res.fraud_probability},
                sort_keys=True,
            ).encode()
        ).hexdigest()

        return FraudGuardInferenceResponse(
            inference_id=inf_res.inference_id,
            tenant_id=inf_res.tenant_id,
            agent_id=inf_res.agent_id,
            transaction_id=inf_res.transaction_id,
            model_name=request.model_name,
            model_version=inf_res.model_version,
            fraud_probability=inf_res.fraud_probability,
            artifact_checksum=reg_manifest.artifact_manifest.checksum,
            request_fingerprint=inf_res.request_fingerprint,
            result_fingerprint=res_hash,
            configuration_hash=inf_res.configuration_hash,
            prediction_timestamp=inf_res.prediction_timestamp,
        )

    # -----------------------------------------------------------------------
    # Phase 264: Risk Intelligence API Service
    # -----------------------------------------------------------------------
    def run_risk_intelligence(
        self,
        tenant_id: uuid.UUID,
        request: FraudGuardRiskIntelligenceRequest,
    ) -> FraudGuardRiskIntelligenceResponse:
        """Orchestrate full FraudGuard risk intelligence pipeline (Phase 264)."""
        logger.info(
            "Executing Risk Intelligence pipeline for tx %s (tenant=%s)",
            request.transaction_id,
            tenant_id,
        )

        # 1. Execute Inference Engine
        feat_dict = dict(zip(request.feature_names, request.feature_values, strict=True))
        inf_req = InferenceRequest(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_name=request.model_name,
            prediction_timestamp=request.prediction_timestamp,
            feature_values=feat_dict,
        )
        inf_res, _ = self.inference_engine.predict_fraud(inf_req)

        # 2. Validate Fraud Probability & Calculate Transaction Risk Score
        prob_res = self.probability_service.process_inference_probability(inf_res)
        tx_risk_res = self.transaction_risk_service.calculate_transaction_risk(
            prob_res, expected_tenant_id=tenant_id, expected_agent_id=request.agent_id
        )

        # 3. Upstream Merchant Risk Signal Processing
        merch_res = None
        if request.merchant_signal:
            merch_res = self.merchant_risk_service.process_merchant_signal(
                request.merchant_signal,
                request.transaction_id,
                request.prediction_timestamp,
                expected_tenant_id=tenant_id,
                expected_agent_id=request.agent_id,
            )

        # 4. Upstream Velocity Risk Signal Processing
        vel_res = None
        if request.velocity_signal:
            vel_res = self.velocity_risk_service.process_velocity_signal(
                request.velocity_signal,
                request.transaction_id,
                request.prediction_timestamp,
                expected_tenant_id=tenant_id,
                expected_agent_id=request.agent_id,
            )

        # 5. Upstream Intent Risk Signal Processing
        intent_res = None
        if request.intent_signal:
            intent_res = self.intent_risk_service.process_intent_signal(
                request.intent_signal,
                request.transaction_id,
                request.prediction_timestamp,
                expected_tenant_id=tenant_id,
                expected_agent_id=request.agent_id,
            )

        # 6. Upstream Policy Evaluation Signal Processing
        policy_res = None
        allow_ml = True
        p_decision = "ALLOW"
        if request.policy_signal:
            policy_res = self.policy_risk_service.process_policy_signal(
                request.policy_signal,
                request.transaction_id,
                request.prediction_timestamp,
                expected_tenant_id=tenant_id,
                expected_agent_id=request.agent_id,
            )
            allow_ml = policy_res.allow_ml_scoring
            p_decision = policy_res.policy_decision

        # 7. Local SHAP Attribution & Local XAI Explanation
        X_mat = np.array([request.feature_values], dtype=np.float32)
        attr_res = self.shap_service.calculate_shap_attributions(
            tenant_id=tenant_id,
            model_name=request.model_name,
            X_matrix=X_mat,
            feature_names=request.feature_names,
            prediction_probability=inf_res.fraud_probability,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            target_model_version=inf_res.model_version,
        )

        local_exp = self.local_xai_service.generate_explanation(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            prediction_timestamp=request.prediction_timestamp,
            inference_result=inf_res,
            transaction_risk_result=tx_risk_res,
            attribution_result=attr_res,
        )

        # 8. Extract Structured Risk Factors
        ext_res = self.extraction_service.extract_risk_factors(
            tenant_id=tenant_id,
            transaction_id=request.transaction_id,
            local_explanation=local_exp,
            policy_result=policy_res,
            merchant_result=merch_res,
            velocity_result=vel_res,
            agent_id=request.agent_id,
        )

        sig_id = uuid.uuid4()
        now = datetime.now(UTC)

        res_payload = {
            "transaction_id": request.transaction_id,
            "tenant_id": str(tenant_id),
            "fraud_probability": inf_res.fraud_probability,
            "risk_score": tx_risk_res.transaction_risk_score,
            "risk_level": tx_risk_res.risk_level,
            "policy_decision": p_decision,
            "allow_ml": allow_ml,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return FraudGuardRiskIntelligenceResponse(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            fraud_probability=inf_res.fraud_probability,
            transaction_risk_score=tx_risk_res.transaction_risk_score,
            risk_level=tx_risk_res.risk_level,
            behaviour_risk=None,
            merchant_risk=merch_res,
            velocity_risk=vel_res,
            intent_risk=intent_res,
            policy_risk=policy_res,
            extracted_factors=ext_res.factors,
            policy_decision=p_decision,
            authoritative=True,
            ml_advisory=True,
            allow_ml_scoring=allow_ml,
            result_fingerprint=res_hash,
            evaluated_at=now,
        )

    # -----------------------------------------------------------------------
    # Phase 261 / 262: XAI Explanation API Service
    # -----------------------------------------------------------------------
    def generate_local_xai(
        self,
        tenant_id: uuid.UUID,
        request: FraudGuardLocalXAIRequest,
    ) -> LocalTransactionExplanation:
        """Orchestrate Local Transaction XAI Explanation (Phase 261)."""
        logger.info(
            "Generating local XAI explanation for tx %s (tenant=%s)",
            request.transaction_id,
            tenant_id,
        )

        # 1. Execute Inference Engine
        feat_dict = dict(zip(request.feature_names, request.feature_values, strict=True))
        inf_req = InferenceRequest(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_name=request.model_name,
            prediction_timestamp=request.prediction_timestamp,
            feature_values=feat_dict,
        )
        inf_res, _ = self.inference_engine.predict_fraud(inf_req)

        # 2. Risk Score Calculation
        prob_res = self.probability_service.process_inference_probability(inf_res)
        tx_risk_res = self.transaction_risk_service.calculate_transaction_risk(
            prob_res, expected_tenant_id=tenant_id, expected_agent_id=request.agent_id
        )

        # 3. SHAP Attributions
        X_mat = np.array([request.feature_values], dtype=np.float32)
        attr_res = self.shap_service.calculate_shap_attributions(
            tenant_id=tenant_id,
            model_name=request.model_name,
            X_matrix=X_mat,
            feature_names=request.feature_names,
            prediction_probability=inf_res.fraud_probability,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            target_model_version=inf_res.model_version,
        )

        # 4. Generate Explanation
        return self.local_xai_service.generate_explanation(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            prediction_timestamp=request.prediction_timestamp,
            inference_result=inf_res,
            transaction_risk_result=tx_risk_res,
            attribution_result=attr_res,
            top_k=request.top_k,
        )

    def generate_global_xai(
        self,
        tenant_id: uuid.UUID,
        request: FraudGuardGlobalXAIRequest,
    ) -> GlobalModelExplanation:
        """Orchestrate Global Model XAI Explanation (Phase 261)."""
        logger.info(
            "Generating global XAI explanation for model %s v%s (tenant=%s)",
            request.model_name,
            request.model_version,
            tenant_id,
        )
        X_mat = np.array(request.sample_features, dtype=np.float32)

        return self.global_xai_service.generate_global_explanation(
            tenant_id=tenant_id,
            model_name=request.model_name,
            target_model_version=request.model_version,
            X_matrix=X_mat,
            feature_names=request.feature_names,
            dataset_fingerprint=request.dataset_fingerprint,
        )

    # -----------------------------------------------------------------------
    # Phase 265: End-to-End FraudGuard Integration
    # -----------------------------------------------------------------------
    def evaluate_transaction(
        self,
        tenant_id: uuid.UUID,
        request: FraudGuardEvaluateRequest,
    ) -> FraudGuardEvaluateResponse:
        """Execute unified end-to-end FraudGuard Evaluation (Phase 265)."""
        logger.info(
            "Executing End-to-End FraudGuard evaluation for tx %s (tenant=%s)",
            request.transaction_id,
            tenant_id,
        )

        # 1. Execute Risk Intelligence Pipeline
        ri_req = FraudGuardRiskIntelligenceRequest(
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_name=request.model_name,
            prediction_timestamp=request.prediction_timestamp,
            feature_names=request.feature_names,
            feature_values=request.feature_values,
            merchant_signal=request.merchant_signal,
            velocity_signal=request.velocity_signal,
            intent_signal=request.intent_signal,
            policy_signal=request.policy_signal,
        )
        ri_res = self.run_risk_intelligence(tenant_id, ri_req)

        # 2. Local XAI Explanation
        local_exp = None
        if request.include_xai:
            xai_req = FraudGuardLocalXAIRequest(
                agent_id=request.agent_id,
                transaction_id=request.transaction_id,
                model_name=request.model_name,
                prediction_timestamp=request.prediction_timestamp,
                feature_names=request.feature_names,
                feature_values=request.feature_values,
                top_k=request.top_k,
            )
            local_exp = self.generate_local_xai(tenant_id, xai_req)

        # 3. Determine Authoritative Decision & Precedence
        authoritative_decision = ri_res.policy_decision
        authoritative_source = "POLICY_ENGINE"

        eval_id = uuid.uuid4()
        now = datetime.now(UTC)

        audit_manifest = {
            "evaluation_id": str(eval_id),
            "tenant_id": str(tenant_id),
            "agent_id": str(request.agent_id),
            "transaction_id": request.transaction_id,
            "authoritative_decision": authoritative_decision,
            "allow_ml_scoring": ri_res.allow_ml_scoring,
            "fraud_probability": ri_res.fraud_probability,
            "transaction_risk_score": ri_res.transaction_risk_score,
            "risk_level": ri_res.risk_level,
            "result_fingerprint": ri_res.result_fingerprint,
            "evaluated_at": now.isoformat(),
        }

        return FraudGuardEvaluateResponse(
            evaluation_id=eval_id,
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            authoritative_decision=authoritative_decision,
            authoritative_source=authoritative_source,
            allow_ml_scoring=ri_res.allow_ml_scoring,
            advisory_risk_intelligence=ri_res,
            local_explanation=local_exp,
            audit_manifest=audit_manifest,
            evaluated_at=now,
        )
