"""Pydantic Transport & Domain Schemas for Risk & Decision Engine Architecture (Phases 266-285)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskSignalType(StrEnum):
    """Strongly typed Risk Signal Type Enum (Phase 266)."""

    AGENTGUARD = "AGENTGUARD"
    FRAUDGUARD = "FRAUDGUARD"
    BEHAVIOUR = "BEHAVIOUR"
    INTENT = "INTENT"
    POLICY = "POLICY"
    MERCHANT = "MERCHANT"
    VELOCITY = "VELOCITY"
    TRANSACTION = "TRANSACTION"


class RiskScoreUnit(StrEnum):
    """Strongly typed Risk Score Unit Enum (Phase 266)."""

    PROBABILITY = "PROBABILITY"
    RISK_SCORE = "RISK_SCORE"
    CONFIDENCE = "CONFIDENCE"
    DECISION = "DECISION"


class RiskEvaluationContext(BaseModel):
    """Canonical Risk Evaluation Context (Phase 266.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative Owning Tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative Target Agent UUID")
    transaction_id: str = Field(..., description="Authoritative Target Transaction ID")
    prediction_timestamp: datetime = Field(
        ..., description="Authoritative Point-in-time Prediction Timestamp UTC"
    )
    request_id: str | None = Field(default=None, description="Optional Request UUID/string")
    correlation_id: str | None = Field(default=None, description="Optional Correlation ID")
    evaluation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Evaluation run UUID")
    source_context: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary immutable context metadata"
    )


class RiskSignal(BaseModel):
    """Canonical Risk Signal Abstraction (Phase 266.2)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    signal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Signal UUID")
    signal_type: RiskSignalType = Field(..., description="Canonical signal type enum")
    source: str = Field(..., description="Source subsystem identifier")
    score: float | None = Field(default=None, description="Raw source numeric score if available")
    score_unit: RiskScoreUnit = Field(..., description="Original score unit classification")
    normalized_score: float | None = Field(
        default=None, description="Canonical normalized risk score [0.0, 100.0] if applicable"
    )
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Signal confidence level [0.0, 1.0]"
    )
    decision: str | None = Field(
        default=None, description="Categorical decision string if applicable"
    )
    timestamp: datetime = Field(..., description="Signal generation timestamp UTC")
    tenant_id: uuid.UUID = Field(..., description="Signal owning tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Signal target agent UUID")
    transaction_id: str = Field(..., description="Signal target transaction ID")
    source_version: str = Field(default="1.0.0", description="Upstream signal version")
    source_fingerprint: str = Field(default="", description="SHA-256 source signal fingerprint")
    availability: bool = Field(default=True, description="Signal availability status flag")
    cold_start: bool = Field(default=False, description="Cold start indicator flag")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata payload map")


class RiskEngineConfig(BaseModel):
    """Immutable Configuration Contract for Risk Engine (Phase 266)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    engine_version: str = Field(default="1.0.0", description="Risk Engine SemVer string")
    configuration_version: str = Field(
        default="1.0.0", description="Risk Engine Configuration Version"
    )
    strict_identity_binding: bool = Field(
        default=True, description="Strict tenant/agent/tx binding flag"
    )
    strict_point_in_time: bool = Field(
        default=True, description="Strict point-in-time timestamp validation flag"
    )
    reject_target_leakage: bool = Field(
        default=True, description="Strict target leakage field rejection flag"
    )


class RiskEngineResult(BaseModel):
    """Governed Risk Engine Outcome Contract (Phase 266.7)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")
    normalized_signals: list[RiskSignal] = Field(
        ..., description="Deterministically ordered normalized risk signals"
    )
    source_fingerprints: list[str] = Field(..., description="Ordered source signal fingerprints")
    configuration_hash: str = Field(..., description="SHA-256 engine configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


class RiskFusionResult(BaseModel):
    """Canonical Risk Fusion Result Contract (Phase 273)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    signals: list[RiskSignal] = Field(
        ..., description="Deterministically ordered canonical normalized risk signals"
    )
    signals_by_type: dict[str, list[RiskSignal]] = Field(
        ..., description="Normalized signals grouped by RiskSignalType string"
    )
    available_signal_types: list[str] = Field(
        ..., description="List of available signal type names"
    )
    unavailable_signal_types: list[str] = Field(
        ..., description="List of unavailable signal type names"
    )

    policy_signals: list[RiskSignal] = Field(
        ..., description="Authoritative control plane policy signals"
    )
    advisory_signals: list[RiskSignal] = Field(
        ..., description="Advisory ML and domain risk signals"
    )
    policy_precedence: str = Field(
        default="NONE",
        description="Policy control plane status (e.g. DENY, ALLOW, REVIEW, NONE)",
    )

    source_fingerprints: list[str] = Field(..., description="Ordered source signal fingerprints")
    configuration_hash: str = Field(..., description="SHA-256 fusion configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


class RiskWeightEntry(BaseModel):
    """Governed weight entry for a single advisory risk signal type (Phase 275)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    signal_type: RiskSignalType = Field(..., description="Target advisory RiskSignalType")
    weight: Decimal = Field(..., gt=0.0, description="Governed positive Decimal weight (> 0.0)")
    description: str = Field(default="", description="Human-readable weight justification")


class RiskWeightConfiguration(BaseModel):
    """Governed Risk Weight Configuration Contract (Phase 275)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    configuration_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Config UUID")
    configuration_version: str = Field(default="1.0.0", description="Configuration SemVer string")
    tenant_id: uuid.UUID | None = Field(default=None, description="Optional tenant-scoped UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Optional agent-scoped UUID")
    weights: dict[str, Decimal] = Field(
        ..., description="Signal type name -> Decimal weight map (> 0.0)"
    )
    effective_from: datetime = Field(
        default_factory=lambda: datetime(2020, 1, 1, tzinfo=UTC),
        description="Effective start timestamp UTC",
    )
    effective_until: datetime | None = Field(
        default=None, description="Optional effective end timestamp UTC"
    )
    description: str = Field(
        default="Governed Advisory Risk Weights", description="Configuration notes"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )

    def compute_hash(self) -> str:
        """Compute canonical SHA-256 hash of weight configuration."""
        sorted_weights = {k: str(v) for k, v in sorted(self.weights.items())}
        payload = {
            "configuration_version": self.configuration_version,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "weights": sorted_weights,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class RiskScoreCalculationResult(BaseModel):
    """Canonical Composite Advisory Risk Score Result Contract (Phase 274)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    composite_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Calculated composite advisory risk score [0.0, 100.0]"
    )
    composite_risk_score_decimal: Decimal = Field(
        ..., description="Exact Decimal composite advisory risk score"
    )
    score_unit: RiskScoreUnit = Field(
        default=RiskScoreUnit.RISK_SCORE, description="Score unit classification"
    )

    included_signal_types: list[str] = Field(..., description="Signal type names included in score")
    excluded_signal_types: list[str] = Field(
        ..., description="Signal type names excluded from score"
    )
    available_signal_types: list[str] = Field(..., description="Available signal type names")
    unavailable_signal_types: list[str] = Field(..., description="Unavailable signal type names")

    applied_weights: dict[str, float] = Field(
        ..., description="Applied weight for each included signal type"
    )
    total_applied_weight: float = Field(..., description="Sum of applied weights")

    weight_configuration_version: str = Field(..., description="Weight config version string")
    weight_configuration_hash: str = Field(..., description="SHA-256 weight config hash")

    source_fingerprints: list[str] = Field(..., description="Ordered source signal fingerprints")
    policy_precedence: str = Field(..., description="Preserved policy precedence string")
    policy_authoritative: bool = Field(
        default=True, description="Policy control plane authority flag"
    )

    calculation_fingerprint: str = Field(..., description="SHA-256 calculation result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


# --- PHASE 276: RISK THRESHOLD CONFIGURATION SCHEMAS ---


class RiskThresholdBand(StrEnum):
    """Non-authoritative risk score classification bands (Phase 276)."""

    LOW_RISK_BAND = "LOW_RISK_BAND"
    MEDIUM_RISK_BAND = "MEDIUM_RISK_BAND"
    HIGH_RISK_BAND = "HIGH_RISK_BAND"


class RiskThresholdConfiguration(BaseModel):
    """Governed Risk Threshold Configuration Contract (Phase 276)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    configuration_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Config UUID")
    configuration_version: str = Field(default="1.0.0", description="Config SemVer string")
    tenant_id: uuid.UUID | None = Field(default=None, description="Optional tenant-scoped UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Optional agent-scoped UUID")

    allow_upper_bound: Decimal = Field(
        default=Decimal("30.0"), description="Upper Decimal bound for LOW_RISK_BAND [0, 100]"
    )
    review_upper_bound: Decimal = Field(
        default=Decimal("70.0"), description="Upper Decimal bound for MEDIUM_RISK_BAND [0, 100]"
    )

    effective_from: datetime = Field(
        default_factory=lambda: datetime(2020, 1, 1, tzinfo=UTC),
        description="Effective start timestamp UTC",
    )
    effective_until: datetime | None = Field(
        default=None, description="Optional effective end timestamp UTC"
    )
    description: str = Field(
        default="Governed Advisory Risk Thresholds", description="Threshold description"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )

    def compute_hash(self) -> str:
        """Compute canonical SHA-256 hash of threshold configuration."""
        payload = {
            "configuration_version": self.configuration_version,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "allow_upper_bound": str(self.allow_upper_bound),
            "review_upper_bound": str(self.review_upper_bound),
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class RiskThresholdEvaluationResult(BaseModel):
    """Canonical Non-Authoritative Risk Threshold Evaluation Result Contract (Phase 276)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Evaluated composite risk score float"
    )
    risk_score_decimal: Decimal = Field(..., description="Exact Decimal composite risk score")

    classification: str = Field(
        ..., description="Non-authoritative threshold classification ('LOW', 'REVIEW_BAND', 'HIGH')"
    )
    matched_threshold_band: RiskThresholdBand = Field(
        ..., description="Matched threshold band enum"
    )

    configuration_version: str = Field(..., description="Threshold configuration version")
    configuration_hash: str = Field(..., description="SHA-256 threshold configuration hash")
    evaluation_fingerprint: str = Field(..., description="SHA-256 evaluation fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


# --- PHASE 277: HARD SECURITY RULES SCHEMAS ---


class HardSecurityRuleType(StrEnum):
    """Strongly typed Hard Security Rule Type Enum (Phase 277)."""

    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    AGENT_MISMATCH = "AGENT_MISMATCH"
    TRANSACTION_MISMATCH = "TRANSACTION_MISMATCH"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    TARGET_LEAKAGE = "TARGET_LEAKAGE"
    POLICY_DENY = "POLICY_DENY"
    POLICY_UNKNOWN = "POLICY_UNKNOWN"
    MISSING_MANDATORY_SIGNAL = "MISSING_MANDATORY_SIGNAL"
    INVALID_RISK_SCORE = "INVALID_RISK_SCORE"
    INVALID_PROBABILITY = "INVALID_PROBABILITY"
    VELOCITY_VIOLATION = "VELOCITY_VIOLATION"
    SECURITY_INVARIANT = "SECURITY_INVARIANT"
    MODEL_INTEGRITY_FAILURE = "MODEL_INTEGRITY_FAILURE"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"


class HardSecurityRuleSeverity(StrEnum):
    """Strongly typed Hard Security Rule Severity Enum (Phase 277)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HardSecurityRuleOutcome(StrEnum):
    """Strongly typed Hard Security Rule Outcome Enum (Phase 277)."""

    PASS = "PASS"
    TRIGGERED = "TRIGGERED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class HardSecurityRuleConfiguration(BaseModel):
    """Governed Hard Security Rule Configuration Contract (Phase 277)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    rule_id: str = Field(..., description="Unique rule identifier e.g. HSR-001")
    rule_version: str = Field(default="1.0.0", description="Rule SemVer string")
    rule_type: HardSecurityRuleType = Field(..., description="Target HardSecurityRuleType")
    severity: HardSecurityRuleSeverity = Field(
        default=HardSecurityRuleSeverity.HIGH, description="Rule severity"
    )
    enabled: bool = Field(default=True, description="Rule enabled status flag")
    tenant_id: uuid.UUID | None = Field(default=None, description="Optional tenant scope UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Optional agent scope UUID")
    effective_from: datetime = Field(
        default_factory=lambda: datetime(2020, 1, 1, tzinfo=UTC),
        description="Effective start timestamp UTC",
    )
    effective_until: datetime | None = Field(
        default=None, description="Optional effective end timestamp UTC"
    )
    description: str = Field(default="", description="Rule justification note")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Rule parameters map")

    def compute_hash(self) -> str:
        """Compute canonical SHA-256 hash of rule configuration."""
        sorted_meta = {k: str(v) for k, v in sorted(self.metadata.items())}
        payload = {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "rule_type": self.rule_type.value,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "metadata": sorted_meta,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class HardSecurityRuleEvaluation(BaseModel):
    """Evaluation result for an individual hard security rule (Phase 277)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    rule_id: str = Field(..., description="Rule identifier e.g. HSR-001")
    rule_version: str = Field(default="1.0.0", description="Rule SemVer string")
    rule_type: HardSecurityRuleType = Field(..., description="Target HardSecurityRuleType")
    severity: HardSecurityRuleSeverity = Field(..., description="Rule severity enum")
    outcome: HardSecurityRuleOutcome = Field(..., description="Rule evaluation outcome enum")

    tenant_id: uuid.UUID = Field(..., description="Signal owning tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Signal target agent UUID")
    transaction_id: str = Field(..., description="Signal target transaction ID")
    prediction_timestamp: datetime = Field(..., description="Evaluation timestamp UTC")

    reason_code: str = Field(..., description="Structured security reason code")
    description: str = Field(default="", description="Detailed outcome justification")
    requires_security_intervention: bool = Field(
        default=False, description="Flag indicating rule triggered security intervention"
    )

    source_fingerprint: str = Field(default="", description="Source payload fingerprint")
    evaluation_fingerprint: str = Field(..., description="SHA-256 rule evaluation fingerprint")


class HardSecurityEvaluationResult(BaseModel):
    """Canonical Fused Hard Security Evaluation Result Contract (Phase 277)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    evaluations: list[HardSecurityRuleEvaluation] = Field(
        ..., description="Deterministically sorted rule evaluations (by severity desc, rule_id asc)"
    )
    triggered_rules: list[HardSecurityRuleEvaluation] = Field(
        ..., description="List of triggered rule evaluations"
    )
    has_triggered_rules: bool = Field(..., description="True if at least one rule triggered")
    max_triggered_severity: HardSecurityRuleSeverity | None = Field(
        default=None, description="Highest severity among triggered rules"
    )

    policy_precedence: str = Field(..., description="Preserved policy precedence string")
    policy_authoritative: bool = Field(default=True, description="Policy authority flag")

    configuration_hash: str = Field(..., description="SHA-256 combined rules configuration hash")
    result_fingerprint: str = Field(..., description="SHA-256 result fingerprint")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


# --- GROUP 7 (PHASES 278-280): FINAL RISK DECISION SCHEMAS ---


class FinalRiskDecision(StrEnum):
    """Strongly typed Authoritative Final Risk Decision Enum (Phases 278-280)."""

    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class FinalRiskDecisionResult(BaseModel):
    """Canonical Authoritative Final Risk Decision Outcome Contract (Phases 278-280)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    decision_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Decision run UUID")

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    decision: FinalRiskDecision = Field(
        ..., description="Authoritative final risk decision (ALLOW, REVIEW, BLOCK)"
    )
    decision_reason: str = Field(..., description="Primary structured machine-readable reason code")

    composite_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Evaluated composite risk score float"
    )
    risk_band: RiskThresholdBand = Field(
        ..., description="Matched non-authoritative risk threshold band"
    )

    policy_precedence: str = Field(..., description="Preserved policy precedence string")
    hard_security_status: str = Field(..., description="Overall hard security status summary")
    triggered_rule_ids: list[str] = Field(
        ..., description="List of triggered hard security rule IDs"
    )

    review_reasons: list[str] = Field(
        ..., description="List of review triggers or justification codes"
    )
    block_reasons: list[str] = Field(
        ..., description="List of block triggers or security violation codes"
    )

    available_signal_types: list[str] = Field(..., description="Available signal type names")
    unavailable_signal_types: list[str] = Field(..., description="Unavailable signal type names")

    cold_start: bool = Field(default=False, description="Cold start indicator flag")
    policy_authoritative: bool = Field(default=True, description="Policy authority flag")

    threshold_configuration_version: str = Field(..., description="Threshold config version")
    threshold_configuration_hash: str = Field(..., description="SHA-256 threshold config hash")

    weight_configuration_version: str = Field(..., description="Weight config version")
    weight_configuration_hash: str = Field(..., description="SHA-256 weight config hash")

    source_fingerprints: list[str] = Field(
        ..., description="Ordered upstream source signal fingerprints"
    )
    calculation_fingerprint: str = Field(..., description="SHA-256 calculation result fingerprint")
    decision_fingerprint: str = Field(..., description="SHA-256 final decision fingerprint")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Result creation timestamp UTC"
    )


# --- GROUP 8 (PHASES 281-285): GOVERNANCE, EXPLANATION, AUDIT, REPLAY & ENFORCEMENT SCHEMAS ---


class DecisionExplanationResult(BaseModel):
    """Canonical Decision Explanation Result Contract (Phase 282)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    evaluation_id: uuid.UUID = Field(..., description="Evaluation run UUID")
    decision_id: uuid.UUID = Field(..., description="Decision run UUID")

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    decision: FinalRiskDecision = Field(..., description="Authoritative final risk decision")
    primary_reason_code: str = Field(
        ..., description="Primary reason code e.g. LOW_RISK_ALLOW_CLEAN"
    )
    primary_reason: str = Field(..., description="Human-readable explanation message")
    contributing_reason_codes: list[str] = Field(
        ..., description="Sorted list of contributing reason codes"
    )
    contributing_reasons: list[str] = Field(
        ..., description="List of contributing explanation strings"
    )

    risk_score: float = Field(..., ge=0.0, le=100.0, description="Evaluated composite risk score")
    threshold_band: RiskThresholdBand = Field(..., description="Matched threshold band")
    policy_precedence: str = Field(..., description="Preserved policy precedence")
    security_rule_summary: str = Field(..., description="Hard security rule evaluation summary")

    cold_start: bool = Field(..., description="Cold start flag")
    unavailable_signal_types: list[str] = Field(..., description="List of unavailable signal types")
    source_fingerprints: list[str] = Field(
        ..., description="Sorted upstream source signal fingerprints"
    )
    decision_fingerprint: str = Field(..., description="SHA-256 final decision fingerprint")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Explanation creation timestamp UTC",
    )


class DecisionAuditEvent(BaseModel):
    """Canonical Append-Only Decision Audit Event Contract (Phase 283)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Audit event UUID")
    decision_id: uuid.UUID = Field(..., description="Target decision UUID")
    evaluation_id: uuid.UUID = Field(..., description="Target evaluation UUID")

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")

    decision: FinalRiskDecision = Field(..., description="Authoritative final risk decision")
    reason_code: str = Field(..., description="Primary reason code string")

    decision_timestamp: datetime = Field(..., description="Decision timestamp UTC")
    prediction_timestamp: datetime = Field(..., description="Prediction timestamp UTC")

    composite_risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite risk score")
    risk_band: RiskThresholdBand = Field(..., description="Matched threshold band")
    policy_precedence: str = Field(..., description="Preserved policy precedence")
    hard_security_status: str = Field(..., description="Hard security status summary")

    cold_start: bool = Field(..., description="Cold start flag")
    unavailable_signal_types: list[str] = Field(..., description="Unavailable signal types")
    source_fingerprints: list[str] = Field(..., description="Sorted source fingerprints")

    weight_configuration_hash: str = Field(..., description="SHA-256 weight config hash")
    threshold_configuration_hash: str = Field(..., description="SHA-256 threshold config hash")
    security_rule_configuration_hash: str = Field(
        ..., description="SHA-256 security rule config hash"
    )
    decision_fingerprint: str = Field(..., description="SHA-256 final decision fingerprint")
    audit_fingerprint: str = Field(..., description="SHA-256 canonical audit event fingerprint")

    engine_version: str = Field(default="1.0.0", description="Risk engine version")
    schema_version: str = Field(default="1.0.0", description="Audit schema version")
    correlation_id: str | None = Field(default=None, description="Optional correlation ID")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Audit event creation timestamp UTC",
    )


class DecisionVerificationStatus(StrEnum):
    """Canonical Decision Verification Status Enum (Phase 284)."""

    VERIFIED = "VERIFIED"
    MISMATCH = "MISMATCH"
    INVALID_INPUT = "INVALID_INPUT"
    UNAVAILABLE = "UNAVAILABLE"


class DecisionVerificationResult(BaseModel):
    """Canonical Decision Replay & Verification Result Contract (Phase 284)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    verification_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Verification run UUID"
    )
    original_decision_id: uuid.UUID = Field(..., description="Target original decision UUID")

    replay_decision: FinalRiskDecision | None = Field(
        default=None, description="Replayed final risk decision if evaluation succeeded"
    )
    original_decision: FinalRiskDecision = Field(..., description="Original authoritative decision")

    decision_match: bool = Field(..., description="True if replayed decision matches original")
    fingerprint_match: bool = Field(
        ..., description="True if replayed fingerprint matches original"
    )
    configuration_match: bool = Field(..., description="True if configuration hashes match")
    provenance_match: bool = Field(..., description="True if source fingerprints match")
    identity_match: bool = Field(..., description="True if tenant/agent/tx identities match")
    timestamp_match: bool = Field(..., description="True if timestamps match")

    verification_status: DecisionVerificationStatus = Field(
        ..., description="Verification status enum"
    )
    mismatch_codes: list[str] = Field(
        default_factory=list, description="List of detected material mismatch codes"
    )
    verification_fingerprint: str = Field(
        ..., description="SHA-256 verification result fingerprint"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Verification creation timestamp UTC",
    )


class EnforcementOutcome(StrEnum):
    """Canonical Decision Enforcement Gate Outcome Enum (Phase 285)."""

    PERMITTED = "PERMITTED"
    SUSPENDED = "SUSPENDED"
    DENIED = "DENIED"


class DecisionEnforcementResult(BaseModel):
    """Canonical Decision Enforcement Gate Result Contract (Phase 285)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    enforcement_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Enforcement run UUID"
    )
    decision_id: uuid.UUID = Field(..., description="Target decision UUID")
    evaluation_id: uuid.UUID = Field(..., description="Target evaluation UUID")

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")

    enforcement_outcome: EnforcementOutcome = Field(
        ..., description="Enforcement gate outcome enum"
    )
    execution_permitted: bool = Field(..., description="True ONLY if ALLOW and all checks pass")
    execution_suspended: bool = Field(..., description="True if decision is REVIEW")
    approval_required: bool = Field(..., description="True if human approval required (REVIEW)")
    authorization_denied: bool = Field(..., description="True if decision is BLOCK")

    reason_code: str = Field(..., description="Structured enforcement reason code")
    enforcement_fingerprint: str = Field(..., description="SHA-256 enforcement result fingerprint")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Enforcement timestamp UTC"
    )
