"""Centralized Hard Security Rules Engine (Phase 277)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from datetime import datetime
from typing import Any

from app.schemas.risk_engine import (
    HardSecurityEvaluationResult,
    HardSecurityRuleConfiguration,
    HardSecurityRuleEvaluation,
    HardSecurityRuleOutcome,
    HardSecurityRuleSeverity,
    HardSecurityRuleType,
    RiskEvaluationContext,
    RiskFusionResult,
    RiskSignal,
    RiskSignalType,
)

logger = logging.getLogger("agentpay.risk.hard_security")

PROHIBITED_TARGET_FIELDS: frozenset[str] = frozenset(
    {
        "is_fraud",
        "fraud_label",
        "post_outcome",
        "chargeback_result",
        "investigation_result",
        "future_outcome",
    }
)

SEVERITY_ORDER: dict[HardSecurityRuleSeverity, int] = {
    HardSecurityRuleSeverity.CRITICAL: 4,
    HardSecurityRuleSeverity.HIGH: 3,
    HardSecurityRuleSeverity.MEDIUM: 2,
    HardSecurityRuleSeverity.LOW: 1,
}

DEFAULT_HARD_RULES: list[HardSecurityRuleConfiguration] = [
    HardSecurityRuleConfiguration(
        rule_id="HSR-001",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.POLICY_DENY,
        severity=HardSecurityRuleSeverity.CRITICAL,
        enabled=True,
        description="Mandatory Security Rule: Triggered on Policy DENY precedence",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-002",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.POLICY_UNKNOWN,
        severity=HardSecurityRuleSeverity.CRITICAL,
        enabled=True,
        description="Mandatory Security Rule: Triggered on UNKNOWN Policy decision",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-003",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.IDENTITY_MISMATCH,
        severity=HardSecurityRuleSeverity.CRITICAL,
        enabled=True,
        description="Mandatory Security Rule: Triggered on tenant/agent/tx identity mismatch",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-004",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.FUTURE_TIMESTAMP,
        severity=HardSecurityRuleSeverity.HIGH,
        enabled=True,
        description="Mandatory Security Rule: Triggered on future signal timestamp",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-005",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.TARGET_LEAKAGE,
        severity=HardSecurityRuleSeverity.CRITICAL,
        enabled=True,
        description="Mandatory Security Rule: Triggered on prohibited target data leakage",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-006",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.INVALID_RISK_SCORE,
        severity=HardSecurityRuleSeverity.HIGH,
        enabled=True,
        description="Mandatory Security Rule: Triggered on invalid score, NaN, or Infinity",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-007",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.MISSING_MANDATORY_SIGNAL,
        severity=HardSecurityRuleSeverity.HIGH,
        enabled=True,
        description="Mandatory Security Rule: Triggered on missing mandatory risk signals",
    ),
    HardSecurityRuleConfiguration(
        rule_id="HSR-008",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.VELOCITY_VIOLATION,
        severity=HardSecurityRuleSeverity.HIGH,
        enabled=True,
        description="Mandatory Security Rule: Triggered on velocity rule violation",
    ),
]


class HardSecurityRulesEngine:
    """Production Centralized Hard Security Rules Engine (Phase 277)."""

    def __init__(
        self,
        rules: list[HardSecurityRuleConfiguration] | None = None,
    ) -> None:
        self.rules = rules if rules is not None else list(DEFAULT_HARD_RULES)
        self._validate_rules(self.rules)

    def _validate_rules(
        self,
        rules: list[HardSecurityRuleConfiguration],
        context: RiskEvaluationContext | None = None,
    ) -> None:
        """Validate hard rule configurations for duplicates, point-in-time, and identity."""
        seen_rule_ids: set[str] = set()
        for rule in rules:
            if rule.rule_id in seen_rule_ids:
                raise ValueError(
                    f"Duplicate rule_id '{rule.rule_id}' detected in hard security rules configuration."  # noqa: E501
                )
            seen_rule_ids.add(rule.rule_id)

            if context is not None:
                if rule.tenant_id and rule.tenant_id != context.tenant_id:
                    raise ValueError(
                        f"Tenant ID mismatch in rule config! Rule tenant '{rule.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
                    )
                if rule.agent_id and rule.agent_id != context.agent_id:
                    raise ValueError(
                        f"Agent ID mismatch in rule config! Rule agent '{rule.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
                    )
                if rule.effective_from > context.prediction_timestamp:
                    raise ValueError(
                        f"Rule '{rule.rule_id}' effective_from '{rule.effective_from.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                    )
                if rule.effective_until and context.prediction_timestamp >= rule.effective_until:
                    raise ValueError(
                        f"Rule '{rule.rule_id}' effective_until '{rule.effective_until.isoformat()}' expired relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
                    )

    def _compute_rule_evaluation_fingerprint(
        self,
        rule_id: str,
        rule_version: str,
        rule_type: str,
        severity: str,
        outcome: str,
        tenant_id: Any,
        agent_id: Any,
        transaction_id: str,
        timestamp: datetime,
        reason_code: str,
    ) -> str:
        payload = {
            "rule_id": rule_id,
            "rule_version": rule_version,
            "rule_type": rule_type,
            "severity": severity,
            "outcome": outcome,
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "timestamp": timestamp.isoformat(),
            "reason_code": reason_code,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def evaluate_rules(
        self,
        context: RiskEvaluationContext,
        signals: list[RiskSignal],
        fused_result: RiskFusionResult | None = None,
        override_rules: list[HardSecurityRuleConfiguration] | None = None,
    ) -> HardSecurityEvaluationResult:
        """Evaluate hard security rules over signals and context deterministically (Phase 277)."""
        rules = override_rules if override_rules is not None else self.rules
        self._validate_rules(rules, context=context)

        # Compute rules configuration hash
        sorted_rule_hashes = sorted([r.compute_hash() for r in rules])
        config_hash = hashlib.sha256(json.dumps(sorted_rule_hashes).encode("utf-8")).hexdigest()

        evaluations: list[HardSecurityRuleEvaluation] = []
        rule_outcomes_map: dict[str, HardSecurityRuleOutcome] = {}

        # Extract context attributes
        policy_precedence = fused_result.policy_precedence if fused_result else "NONE"

        for rule in rules:
            if not rule.enabled:
                continue

            outcome = HardSecurityRuleOutcome.PASS
            reason_code = "RULE_PASSED"
            desc = f"Hard security rule '{rule.rule_id}' passed successfully."
            triggered_intervention = False
            src_fp = ""

            # 1. HSR-001: POLICY_DENY
            if rule.rule_type == HardSecurityRuleType.POLICY_DENY:
                if policy_precedence == "DENY":
                    outcome = HardSecurityRuleOutcome.TRIGGERED
                    reason_code = "POLICY_DENY_TRIGGERED"
                    desc = "Authoritative Policy DENY control signal detected."
                    triggered_intervention = True

            # 2. HSR-002: POLICY_UNKNOWN
            elif rule.rule_type == HardSecurityRuleType.POLICY_UNKNOWN:
                for sig in signals:
                    if (
                        sig.signal_type == RiskSignalType.POLICY
                        and sig.decision
                        and sig.decision.upper() == "UNKNOWN"
                    ):
                        outcome = HardSecurityRuleOutcome.TRIGGERED
                        reason_code = "POLICY_UNKNOWN_TRIGGERED"
                        desc = "Unrecognized or UNKNOWN policy decision encountered."
                        triggered_intervention = True
                        src_fp = sig.source_fingerprint
                        break

            # 3. HSR-003: IDENTITY_MISMATCH
            elif rule.rule_type == HardSecurityRuleType.IDENTITY_MISMATCH:
                for sig in signals:
                    if (
                        sig.tenant_id != context.tenant_id
                        or sig.agent_id != context.agent_id
                        or sig.transaction_id != context.transaction_id
                    ):
                        outcome = HardSecurityRuleOutcome.TRIGGERED
                        reason_code = "IDENTITY_MISMATCH_TRIGGERED"
                        desc = f"Signal '{sig.signal_id}' identity mismatch against evaluation context."  # noqa: E501
                        triggered_intervention = True
                        src_fp = sig.source_fingerprint
                        break

            # 4. HSR-004: FUTURE_TIMESTAMP
            elif rule.rule_type == HardSecurityRuleType.FUTURE_TIMESTAMP:
                for sig in signals:
                    if sig.timestamp > context.prediction_timestamp:
                        outcome = HardSecurityRuleOutcome.TRIGGERED
                        reason_code = "FUTURE_TIMESTAMP_TRIGGERED"
                        desc = f"Signal timestamp '{sig.timestamp.isoformat()}' is in the future."
                        triggered_intervention = True
                        src_fp = sig.source_fingerprint
                        break

            # 5. HSR-005: TARGET_LEAKAGE
            elif rule.rule_type == HardSecurityRuleType.TARGET_LEAKAGE:
                for sig in signals:
                    if sig.metadata:
                        for k, v in sig.metadata.items():
                            k_lower = str(k).lower()
                            v_str = str(v).lower()
                            if k_lower in PROHIBITED_TARGET_FIELDS or any(
                                tf in v_str for tf in PROHIBITED_TARGET_FIELDS
                            ):
                                outcome = HardSecurityRuleOutcome.TRIGGERED
                                reason_code = "TARGET_LEAKAGE_TRIGGERED"
                                desc = f"Prohibited target leakage field '{k}' in signal metadata."
                                triggered_intervention = True
                                src_fp = sig.source_fingerprint
                                break
                    if outcome == HardSecurityRuleOutcome.TRIGGERED:
                        break

            # 6. HSR-006: INVALID_RISK_SCORE
            elif rule.rule_type == HardSecurityRuleType.INVALID_RISK_SCORE:
                for sig in signals:
                    if sig.score is not None:
                        val_float = float(sig.score)
                        if (
                            math.isnan(val_float)
                            or math.isinf(val_float)
                            or val_float < 0.0
                            or val_float > 100.0
                        ):
                            outcome = HardSecurityRuleOutcome.TRIGGERED
                            reason_code = "INVALID_RISK_SCORE_TRIGGERED"
                            desc = f"Invalid numeric score value {val_float} detected."
                            triggered_intervention = True
                            src_fp = sig.source_fingerprint
                            break

            # 7. HSR-007: MISSING_MANDATORY_SIGNAL
            elif rule.rule_type == HardSecurityRuleType.MISSING_MANDATORY_SIGNAL:
                mandatory_types = rule.metadata.get(
                    "mandatory_signal_types", [RiskSignalType.FRAUDGUARD.value]
                )
                available_types = (
                    fused_result.available_signal_types
                    if fused_result
                    else [s.signal_type.value for s in signals if s.availability]
                )
                for mt in mandatory_types:
                    if mt not in available_types:
                        outcome = HardSecurityRuleOutcome.TRIGGERED
                        reason_code = "MISSING_MANDATORY_SIGNAL_TRIGGERED"
                        desc = f"Mandatory signal type '{mt}' is missing or unavailable."
                        triggered_intervention = True
                        break

            # 8. HSR-008: VELOCITY_VIOLATION
            elif rule.rule_type == HardSecurityRuleType.VELOCITY_VIOLATION:
                max_velocity_score = rule.metadata.get("max_velocity_score", 90.0)
                for sig in signals:
                    if (
                        sig.signal_type == RiskSignalType.VELOCITY
                        and sig.normalized_score is not None
                        and sig.normalized_score >= max_velocity_score
                    ):
                        outcome = HardSecurityRuleOutcome.TRIGGERED
                        reason_code = "VELOCITY_VIOLATION_TRIGGERED"
                        desc = f"Velocity risk score {sig.normalized_score} exceeded limit {max_velocity_score}."  # noqa: E501
                        triggered_intervention = True
                        src_fp = sig.source_fingerprint
                        break

            # Deduplication & Conflict Detection
            if rule.rule_id in rule_outcomes_map:
                if rule_outcomes_map[rule.rule_id] != outcome:
                    raise ValueError(
                        f"Conflicting rule outcomes for rule_id '{rule.rule_id}': {rule_outcomes_map[rule.rule_id]} != {outcome}"  # noqa: E501
                    )
                continue
            rule_outcomes_map[rule.rule_id] = outcome

            eval_fp = self._compute_rule_evaluation_fingerprint(
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                rule_type=rule.rule_type.value,
                severity=rule.severity.value,
                outcome=outcome.value,
                tenant_id=context.tenant_id,
                agent_id=context.agent_id,
                transaction_id=context.transaction_id,
                timestamp=context.prediction_timestamp,
                reason_code=reason_code,
            )

            evaluations.append(
                HardSecurityRuleEvaluation(
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    rule_type=rule.rule_type,
                    severity=rule.severity,
                    outcome=outcome,
                    tenant_id=context.tenant_id,
                    agent_id=context.agent_id,
                    transaction_id=context.transaction_id,
                    prediction_timestamp=context.prediction_timestamp,
                    reason_code=reason_code,
                    description=desc,
                    requires_security_intervention=triggered_intervention,
                    source_fingerprint=src_fp,
                    evaluation_fingerprint=eval_fp,
                )
            )

        # Deterministic sorting: Primary by severity descending, Secondary by rule_id ascending
        evaluations.sort(key=lambda e: (-SEVERITY_ORDER.get(e.severity, 0), e.rule_id))

        triggered_rules = [e for e in evaluations if e.outcome == HardSecurityRuleOutcome.TRIGGERED]
        has_triggered = len(triggered_rules) > 0

        max_severity: HardSecurityRuleSeverity | None = None
        if has_triggered:
            max_severity = max(
                triggered_rules, key=lambda e: SEVERITY_ORDER.get(e.severity, 0)
            ).severity  # noqa: E501

        # Compute SHA-256 result fingerprint
        eval_payloads = [
            {
                "rule_id": e.rule_id,
                "rule_version": e.rule_version,
                "rule_type": e.rule_type.value,
                "severity": e.severity.value,
                "outcome": e.outcome.value,
                "evaluation_fingerprint": e.evaluation_fingerprint,
            }
            for e in evaluations
        ]
        res_payload = {
            "evaluation_id": str(context.evaluation_id),
            "tenant_id": str(context.tenant_id),
            "agent_id": str(context.agent_id),
            "transaction_id": context.transaction_id,
            "prediction_timestamp": context.prediction_timestamp.isoformat(),
            "policy_precedence": policy_precedence,
            "has_triggered_rules": has_triggered,
            "max_triggered_severity": max_severity.value if max_severity else None,
            "configuration_hash": config_hash,
            "evaluations": eval_payloads,
        }
        res_fp = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode("utf-8")).hexdigest()  # noqa: E501

        return HardSecurityEvaluationResult(
            evaluation_id=context.evaluation_id,
            tenant_id=context.tenant_id,
            agent_id=context.agent_id,
            transaction_id=context.transaction_id,
            prediction_timestamp=context.prediction_timestamp,
            evaluations=evaluations,
            triggered_rules=triggered_rules,
            has_triggered_rules=has_triggered,
            max_triggered_severity=max_severity,
            policy_precedence=policy_precedence,
            policy_authoritative=True,
            configuration_hash=config_hash,
            result_fingerprint=res_fp,
        )
