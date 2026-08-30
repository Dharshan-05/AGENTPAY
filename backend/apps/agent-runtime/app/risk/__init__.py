"""Risk & Decision Engine Package (Phases 266-285)."""

from __future__ import annotations

from app.risk.audit.decision_audit import DecisionAuditEventBuilder, DecisionAuditEventService
from app.risk.decisions.allow_decision import AllowDecisionEngine
from app.risk.decisions.block_decision import BlockDecisionEngine
from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.risk.decisions.decision_explanation import DecisionExplanationEngine
from app.risk.decisions.enforcement_gate import DecisionEnforcementGate
from app.risk.decisions.review_decision import ReviewDecisionEngine
from app.risk.hard_security_rules import DEFAULT_HARD_RULES, HardSecurityRulesEngine
from app.risk.integrations.agentguard_risk import AgentGuardRiskIntegrationService
from app.risk.integrations.behaviour_risk import BehaviourRiskIntegrationService
from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.integrations.intent_risk import IntentRiskIntegrationService
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.replay.decision_replay import DecisionReplayEngine, DecisionVerificationService
from app.risk.risk_config import compute_configuration_hash
from app.risk.risk_engine import RiskEngine
from app.risk.risk_fusion import RiskFusionEngine
from app.risk.risk_score_calculator import RiskScoreCalculator
from app.risk.risk_thresholds import RiskThresholdService
from app.risk.risk_weights import DEFAULT_GOVERNED_WEIGHTS, RiskWeightService
from app.risk.signal_normalizer import RiskSignalNormalizer

__all__ = [
    "DEFAULT_GOVERNED_WEIGHTS",
    "DEFAULT_HARD_RULES",
    "AgentGuardRiskIntegrationService",
    "AllowDecisionEngine",
    "BehaviourRiskIntegrationService",
    "BlockDecisionEngine",
    "DecisionAuditEventBuilder",
    "DecisionAuditEventService",
    "DecisionEnforcementGate",
    "DecisionExplanationEngine",
    "DecisionReplayEngine",
    "DecisionVerificationService",
    "FinalRiskDecisionEngine",
    "FraudGuardRiskIntegrationService",
    "HardSecurityRulesEngine",
    "IntentRiskIntegrationService",
    "PolicyRiskIntegrationService",
    "ReviewDecisionEngine",
    "RiskEngine",
    "RiskFusionEngine",
    "RiskScoreCalculator",
    "RiskSignalNormalizer",
    "RiskThresholdService",
    "RiskWeightService",
    "compute_configuration_hash",
]
