"""Risk Decision Application Service (Phase 284)."""

from __future__ import annotations

import logging
import uuid

from app.risk.audit.decision_audit import DecisionAuditEventService
from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.risk.decisions.decision_explanation import DecisionExplanationEngine
from app.risk.hard_security_rules import HardSecurityRulesEngine
from app.risk.risk_fusion import RiskFusionEngine
from app.risk.risk_score_calculator import RiskScoreCalculator
from app.risk.risk_thresholds import RiskThresholdService
from app.risk.signal_normalizer import RiskSignalNormalizer
from app.schemas.risk_decision_api import (
    RiskDecisionEvaluateRequest,
    RiskDecisionEvaluateResponse,
)
from app.schemas.risk_engine import (
    DecisionAuditEvent,
    RiskEvaluationContext,
)

logger = logging.getLogger("agentpay.application.services.risk_decision")


class RiskDecisionApplicationService:
    """Application orchestration service for Risk Decision API (Phase 284)."""

    def __init__(
        self,
        normalizer: RiskSignalNormalizer | None = None,
        fusion_engine: RiskFusionEngine | None = None,
        score_calculator: RiskScoreCalculator | None = None,
        threshold_service: RiskThresholdService | None = None,
        security_engine: HardSecurityRulesEngine | None = None,
        decision_engine: FinalRiskDecisionEngine | None = None,
        explanation_engine: DecisionExplanationEngine | None = None,
        audit_service: DecisionAuditEventService | None = None,
    ) -> None:
        self.normalizer = normalizer or RiskSignalNormalizer()
        self.fusion_engine = fusion_engine or RiskFusionEngine()
        self.score_calculator = score_calculator or RiskScoreCalculator()
        self.threshold_service = threshold_service or RiskThresholdService()
        self.security_engine = security_engine or HardSecurityRulesEngine()
        self.decision_engine = decision_engine or FinalRiskDecisionEngine()
        self.explanation_engine = explanation_engine or DecisionExplanationEngine()
        self.audit_service = audit_service or DecisionAuditEventService()

    def evaluate_risk_decision(
        self,
        tenant_id: uuid.UUID,
        request: RiskDecisionEvaluateRequest,
    ) -> RiskDecisionEvaluateResponse:
        """Orchestrate authoritative risk decision evaluation, explanation, and audit recording."""
        logger.info(
            "Evaluating risk decision API request for agent %s (tx=%s, tenant=%s)",
            request.agent_id,
            request.transaction_id,
            tenant_id,
        )

        # 1. Establish Authoritative Evaluation Context
        context = RiskEvaluationContext(
            tenant_id=tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            prediction_timestamp=request.prediction_timestamp,
            source_context=request.context_metadata,
        )

        # 2. Validate Tenant/Agent/Tx Identity on Input Signals
        for sig in request.signals:
            if sig.tenant_id != tenant_id:
                raise ValueError(
                    f"Tenant ID mismatch in signal '{sig.signal_id}'! Signal tenant '{sig.tenant_id}' != request tenant '{tenant_id}'"  # noqa: E501
                )
            if sig.agent_id != request.agent_id:
                raise ValueError(
                    f"Agent ID mismatch in signal '{sig.signal_id}'! Signal agent '{sig.agent_id}' != request agent '{request.agent_id}'"  # noqa: E501
                )
            if sig.transaction_id != request.transaction_id:
                raise ValueError(
                    f"Transaction ID mismatch in signal '{sig.signal_id}'! Signal tx '{sig.transaction_id}' != request tx '{request.transaction_id}'"  # noqa: E501
                )

        # 3. Signal Normalization
        norm_signals = self.normalizer.normalize_signals(request.signals, context=context)

        # 4. Signal Fusion
        fused_res = self.fusion_engine.fuse(context, norm_signals)

        # 5. Composite Risk Score Calculation
        calc_res = self.score_calculator.calculate_score(fused_res, context=context)

        # 6. Non-Authoritative Threshold Evaluation
        thresh_res = self.threshold_service.evaluate_thresholds(calc_res, context=context)

        # 7. Hard Security Rules Engine Evaluation
        sec_res = self.security_engine.evaluate_rules(context, norm_signals, fused_result=fused_res)

        # 8. Final Authoritative Risk Decision Evaluation
        final_dec = self.decision_engine.evaluate_final_decision(
            context, calc_res, thresh_res, sec_res
        )

        # 9. Decision Explanation Engine
        explanation = self.explanation_engine.explain_decision(final_dec)

        # 10. Append-Only Decision Audit Event Recording
        audit_event = self.audit_service.record_decision_event(
            decision_result=final_dec,
            security_result=sec_res,
        )

        # 11. Build Safe API Response
        return RiskDecisionEvaluateResponse(
            evaluation_id=final_dec.evaluation_id,
            decision_id=final_dec.decision_id,
            tenant_id=final_dec.tenant_id,
            agent_id=final_dec.agent_id,
            transaction_id=final_dec.transaction_id,
            decision=final_dec.decision,
            reason_code=final_dec.decision_reason,
            risk_score=final_dec.composite_risk_score,
            risk_band=final_dec.risk_band,
            policy_precedence=final_dec.policy_precedence,
            hard_security_status=final_dec.hard_security_status,
            cold_start=final_dec.cold_start,
            unavailable_signal_types=final_dec.unavailable_signal_types,
            explanation=explanation,
            audit_event=audit_event,
            decision_fingerprint=final_dec.decision_fingerprint,
        )

    def get_audit_event(
        self, tenant_id: uuid.UUID, decision_id: uuid.UUID
    ) -> DecisionAuditEvent | None:
        """Retrieve audit event by decision ID under tenant isolation."""
        return self.audit_service.get_event_by_id(tenant_id, decision_id)
