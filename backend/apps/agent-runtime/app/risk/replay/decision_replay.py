"""Decision Replay & Deterministic Verification Engine (Phase 284)."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.risk.hard_security_rules import HardSecurityRulesEngine
from app.risk.risk_fusion import RiskFusionEngine
from app.risk.risk_score_calculator import RiskScoreCalculator
from app.risk.risk_thresholds import RiskThresholdService
from app.risk.risk_weights import RiskWeightService
from app.schemas.risk_engine import (
    DecisionVerificationResult,
    DecisionVerificationStatus,
    FinalRiskDecisionResult,
    HardSecurityRuleConfiguration,
    RiskEvaluationContext,
    RiskSignal,
    RiskThresholdConfiguration,
    RiskWeightConfiguration,
)

logger = logging.getLogger("agentpay.risk.replay.decision")


class DecisionReplayEngine:
    """Production Decision Replay Engine (Phase 284).

    Re-runs canonical risk pipeline components using original signals and configurations
    to verify deterministic replay accuracy without mutating production state.
    """

    def __init__(
        self,
        fusion_engine: RiskFusionEngine | None = None,
        score_calculator: RiskScoreCalculator | None = None,
        weight_service: RiskWeightService | None = None,
        threshold_service: RiskThresholdService | None = None,
        security_engine: HardSecurityRulesEngine | None = None,
        decision_engine: FinalRiskDecisionEngine | None = None,
    ) -> None:
        self.fusion_engine = fusion_engine or RiskFusionEngine()
        self.score_calculator = score_calculator or RiskScoreCalculator()
        self.weight_service = weight_service or RiskWeightService()
        self.threshold_service = threshold_service or RiskThresholdService()
        self.security_engine = security_engine or HardSecurityRulesEngine()
        self.decision_engine = decision_engine or FinalRiskDecisionEngine()

    def replay_evaluation(
        self,
        context: RiskEvaluationContext,
        signals: list[RiskSignal],
        weight_config: RiskWeightConfiguration | None = None,
        threshold_config: RiskThresholdConfiguration | None = None,
        rules_config: list[HardSecurityRuleConfiguration] | None = None,
    ) -> FinalRiskDecisionResult:
        """Replay canonical risk decision evaluation pipeline (Phase 284)."""
        logger.info(
            "Replaying decision evaluation for context %s (tx=%s)",
            context.evaluation_id,
            context.transaction_id,
        )

        fused_res = self.fusion_engine.fuse(context, signals)
        calc_res = self.score_calculator.calculate_score(
            fused_res, context=context, weight_config=weight_config
        )
        thresh_res = self.threshold_service.evaluate_thresholds(
            calc_res, context=context, override_config=threshold_config
        )
        sec_engine = (
            HardSecurityRulesEngine(rules=rules_config)
            if rules_config is not None
            else self.security_engine
        )
        sec_res = sec_engine.evaluate_rules(context, signals, fused_result=fused_res)

        return self.decision_engine.evaluate_final_decision(context, calc_res, thresh_res, sec_res)


class DecisionVerificationService:
    """Service performing deterministic verification of decision replay (Phase 284)."""

    def __init__(self, replay_engine: DecisionReplayEngine | None = None) -> None:
        self.replay_engine = replay_engine or DecisionReplayEngine()

    def _compute_verification_fingerprint(
        self,
        verification_id: Any,
        original_decision_id: Any,
        decision_match: bool,
        fingerprint_match: bool,
        configuration_match: bool,
        provenance_match: bool,
        identity_match: bool,
        timestamp_match: bool,
        verification_status: str,
        mismatch_codes: list[str],
    ) -> str:
        """Compute SHA-256 fingerprint for verification outcome."""
        payload = {
            "verification_id": str(verification_id),
            "original_decision_id": str(original_decision_id),
            "decision_match": decision_match,
            "fingerprint_match": fingerprint_match,
            "configuration_match": configuration_match,
            "provenance_match": provenance_match,
            "identity_match": identity_match,
            "timestamp_match": timestamp_match,
            "verification_status": verification_status,
            "mismatch_codes": sorted(mismatch_codes),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def verify_decision(
        self,
        original_decision: FinalRiskDecisionResult,
        context: RiskEvaluationContext,
        signals: list[RiskSignal],
        weight_config: RiskWeightConfiguration | None = None,
        threshold_config: RiskThresholdConfiguration | None = None,
        rules_config: list[HardSecurityRuleConfiguration] | None = None,
    ) -> DecisionVerificationResult:
        """Perform deterministic replay and verification against original decision (Phase 284)."""
        mismatch_codes: list[str] = []

        try:
            replayed = self.replay_engine.replay_evaluation(
                context=context,
                signals=signals,
                weight_config=weight_config,
                threshold_config=threshold_config,
                rules_config=rules_config,
            )
            replay_dec = replayed.decision
        except Exception as exc:
            logger.warning("Replay execution failed: %s", exc)
            mismatch_codes.append(f"REPLAY_EXECUTION_ERROR_{type(exc).__name__}")
            vf_fp = self._compute_verification_fingerprint(
                verification_id=uuid_gen(),
                original_decision_id=original_decision.decision_id,
                decision_match=False,
                fingerprint_match=False,
                configuration_match=False,
                provenance_match=False,
                identity_match=False,
                timestamp_match=False,
                verification_status=DecisionVerificationStatus.INVALID_INPUT.value,
                mismatch_codes=mismatch_codes,
            )
            return DecisionVerificationResult(
                original_decision_id=original_decision.decision_id,
                replay_decision=None,
                original_decision=original_decision.decision,
                decision_match=False,
                fingerprint_match=False,
                configuration_match=False,
                provenance_match=False,
                identity_match=False,
                timestamp_match=False,
                verification_status=DecisionVerificationStatus.INVALID_INPUT,
                mismatch_codes=mismatch_codes,
                verification_fingerprint=vf_fp,
            )

        # Identity Checks
        id_match = (
            replayed.tenant_id == original_decision.tenant_id
            and replayed.agent_id == original_decision.agent_id
            and replayed.transaction_id == original_decision.transaction_id
        )
        if not id_match:
            mismatch_codes.append("IDENTITY_MISMATCH")

        # Timestamp Check
        ts_match = replayed.prediction_timestamp == original_decision.prediction_timestamp
        if not ts_match:
            mismatch_codes.append("PREDICTION_TIMESTAMP_MISMATCH")

        # Decision Match
        dec_match = replayed.decision == original_decision.decision
        if not dec_match:
            mismatch_codes.append(
                f"DECISION_MISMATCH_{original_decision.decision.value}_VS_{replayed.decision.value}"
            )

        # Score & Reason Match
        if abs(replayed.composite_risk_score - original_decision.composite_risk_score) > 1e-6:
            mismatch_codes.append("COMPOSITE_RISK_SCORE_MISMATCH")

        if replayed.decision_reason != original_decision.decision_reason:
            mismatch_codes.append("DECISION_REASON_MISMATCH")

        # Configuration Match
        config_match = (
            replayed.weight_configuration_hash == original_decision.weight_configuration_hash
            and replayed.threshold_configuration_hash
            == original_decision.threshold_configuration_hash  # noqa: E501
        )
        if not config_match:
            mismatch_codes.append("CONFIGURATION_HASH_MISMATCH")

        # Provenance Match
        prov_match = sorted(replayed.source_fingerprints) == sorted(
            original_decision.source_fingerprints
        )  # noqa: E501
        if not prov_match:
            mismatch_codes.append("SOURCE_FINGERPRINTS_MISMATCH")

        # Fingerprint Match
        fp_match = replayed.decision_fingerprint == original_decision.decision_fingerprint
        if not fp_match:
            mismatch_codes.append("DECISION_FINGERPRINT_MISMATCH")

        # Overall Status
        all_ok = (
            id_match
            and ts_match
            and dec_match
            and config_match
            and prov_match
            and fp_match
            and not mismatch_codes
        )
        status = (
            DecisionVerificationStatus.VERIFIED if all_ok else DecisionVerificationStatus.MISMATCH
        )

        ver_id = uuid_gen()
        vf_fp = self._compute_verification_fingerprint(
            verification_id=ver_id,
            original_decision_id=original_decision.decision_id,
            decision_match=dec_match,
            fingerprint_match=fp_match,
            configuration_match=config_match,
            provenance_match=prov_match,
            identity_match=id_match,
            timestamp_match=ts_match,
            verification_status=status.value,
            mismatch_codes=mismatch_codes,
        )

        return DecisionVerificationResult(
            verification_id=ver_id,
            original_decision_id=original_decision.decision_id,
            replay_decision=replay_dec,
            original_decision=original_decision.decision,
            decision_match=dec_match,
            fingerprint_match=fp_match,
            configuration_match=config_match,
            provenance_match=prov_match,
            identity_match=id_match,
            timestamp_match=ts_match,
            verification_status=status,
            mismatch_codes=mismatch_codes,
            verification_fingerprint=vf_fp,
        )


def uuid_gen() -> Any:
    import uuid

    return uuid.uuid4()
