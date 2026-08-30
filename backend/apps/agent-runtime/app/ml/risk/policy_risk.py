"""Policy Risk Score Service with Strict Policy Precedence (Phase 255)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.policy_evaluation import PolicyEvaluationResult

logger = logging.getLogger("fraudguard.ml.risk.policy")


class PolicyRiskScoreService:
    """Governed Policy Risk Intelligence Service enforcing Policy Precedence (Phase 255)."""

    def process_policy_signal(
        self,
        policy_result: PolicyEvaluationResult | dict[str, Any],
        transaction_id: str,
        prediction_timestamp: datetime,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
    ) -> PolicyRiskResult:
        """Process upstream policy evaluation result into PolicyRiskResult enforcing DENY precedence (Phase 255)."""  # noqa: E501
        logger.info("Processing policy risk signal for transaction %s", transaction_id)

        agent_id: uuid.UUID | None = None
        if isinstance(policy_result, PolicyEvaluationResult):
            tenant_id = policy_result.tenant_id
            agent_id = policy_result.agent_id
            decision = policy_result.decision
            decision_code = (
                policy_result.reason_codes[0] if policy_result.reason_codes else "POLICY_EVALUATED"
            )  # noqa: E501
            reason_count = len(policy_result.reason_codes)
            sig_time = policy_result.evaluated_at
        elif isinstance(policy_result, dict):
            tenant_id = uuid.UUID(str(policy_result["tenant_id"]))
            agent_id = (
                uuid.UUID(str(policy_result["agent_id"])) if policy_result.get("agent_id") else None
            )  # noqa: E501
            decision = str(policy_result.get("decision", "UNKNOWN"))
            decision_code = str(policy_result.get("decision_code", "POLICY_EVALUATED"))
            reason_count = int(policy_result.get("reason_count", 0))
            raw_sig_time = policy_result.get("evaluated_at", datetime.now(UTC))
            if isinstance(raw_sig_time, str):
                sig_time = datetime.fromisoformat(raw_sig_time)
            else:
                sig_time = raw_sig_time
        else:
            raise ValueError("Unsupported policy signal input type.")

        # 1. Unknown / Unverified Policy Decision Rejection (Fail-Closed)
        if not decision or decision == "UNKNOWN":
            logger.error(
                "Policy decision is UNKNOWN or unverified for transaction %s", transaction_id
            )  # noqa: E501
            raise ValueError("Policy decision is UNKNOWN or unverified! Fail-closed enforced.")

        # 2. Isolation Validation
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {expected_tenant_id}, got {tenant_id}")

        if expected_agent_id and agent_id and agent_id != expected_agent_id:
            raise ValueError(f"Agent mismatch! Expected {expected_agent_id}, got {agent_id}")

        # 3. Point-in-Time Safety
        p_time = (
            prediction_timestamp.replace(tzinfo=UTC)
            if prediction_timestamp.tzinfo is None
            else prediction_timestamp
        )  # noqa: E501
        s_time = sig_time.replace(tzinfo=UTC) if sig_time.tzinfo is None else sig_time

        if s_time > p_time:
            raise ValueError("Point-in-time violation: policy signal timestamp is in the future!")

        # 4. Authoritative Policy Decision Precedence & Score Assignment
        if decision == "DENY":
            risk_score = 100.0
            allow_ml = False  # POLICY DENY strictly forbids downstream ML authorization override!
        elif decision == "REQUIRE_APPROVAL":
            risk_score = 50.0
            allow_ml = True
        elif decision in ("ALLOW", "NO_APPLICABLE_POLICY"):
            risk_score = 0.0
            allow_ml = True
        else:
            raise ValueError(f"Unrecognized policy decision state '{decision}'")

        sig_id = uuid.uuid4()

        cfg_payload = {
            "version": "1.0.0",
            "source": "AGENTGUARD_POLICY_ENGINE",
            "authoritative": True,
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        src_payload = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id) if agent_id else None,
            "decision": decision,
            "decision_code": decision_code,
            "reason_count": reason_count,
            "signal_timestamp": s_time.isoformat(),
        }
        src_hash = hashlib.sha256(json.dumps(src_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "policy_risk_score": risk_score,
            "policy_decision": decision,
            "allow_ml_scoring": allow_ml,
            "tenant_id": str(tenant_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return PolicyRiskResult(
            risk_signal_id=sig_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            policy_risk_score=risk_score,
            policy_decision=decision,
            policy_decision_code=decision_code,
            policy_reason_count=reason_count,
            authoritative=True,
            ml_advisory=True,
            allow_ml_scoring=allow_ml,
            source="AGENTGUARD_POLICY_ENGINE",
            signal_timestamp=s_time,
            prediction_timestamp=p_time,
            configuration_hash=cfg_hash,
            source_fingerprint=src_hash,
            result_fingerprint=res_hash,
        )
