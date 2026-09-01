"""Plan Validation application service for AGENTPAY (Phase 148).

Responsibilities:
    - Fail-closed validation of AgentPlan representations
    - Validate schema completeness, identity consistency, sequence contiguousness
    - Validate dependency graph integrity and perform cycle detection (DAG)
    - Validate action taxonomy alignment
    - Detect secret leakage in steps, inputs, targets, and constraints
    - Enforce UNKNOWN intent execution eligibility invariant (execution_eligible = False)
    - FAIL-CLOSED: Rejects malformed or dangerous plans
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import Any

from app.schemas.plans import AgentPlan, PlanValidationResult

logger = logging.getLogger("agentpay.agent.plan_validation.service")

# Supported canonical action taxonomy
SUPPORTED_PLAN_ACTIONS = frozenset(
    {
        "validate_intent",
        "lookup_merchant",
        "check_constraints",
        "request_authorization",
        "prepare_payment",
        "lookup_transaction",
        "verify_refund_eligibility",
        "prepare_refund",
        "query_transaction_records",
        "query_account_balance",
        "query_merchant_catalog",
        "query_user_profile",
        "inspect_agent_configuration",
        "reject_unknown_intent",
    }
)

# Secret detection pattern for fail-closed validation
FORBIDDEN_SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|access_token|refresh_token|bearer\s+[a-z0-9\-\._~\+\/]+=*|api_key|private_key)"  # noqa: E501
)


class PlanValidationService:
    """Application service for validating Agent Plans fail-closed (Phase 148)."""

    def _scan_for_secrets(self, data: Any, path: str, errors: list[str]) -> None:
        """Recursively scan payload data structures for secret material."""
        if isinstance(data, str):
            if FORBIDDEN_SECRET_PATTERN.search(data):
                errors.append(f"Secret material detected at '{path}'.")
        elif isinstance(data, dict):
            for k, v in data.items():
                if FORBIDDEN_SECRET_PATTERN.search(str(k)):
                    errors.append(f"Secret key name '{k}' detected at '{path}'.")
                self._scan_for_secrets(v, f"{path}.{k}", errors)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                self._scan_for_secrets(item, f"{path}[{idx}]", errors)

    def validate_plan(
        self,
        plan: AgentPlan,
        target_tenant_id: uuid.UUID | None = None,
        target_agent_id: uuid.UUID | None = None,
    ) -> PlanValidationResult:
        """Perform comprehensive fail-closed validation of an AgentPlan.

        Returns PlanValidationResult.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not plan:
            return PlanValidationResult(
                is_valid=True,
                errors=[],
                warnings=["No execution plan steps to validate."],
            )

        # 1. Identity & Scope Consistency
        if target_tenant_id and plan.tenant_id != target_tenant_id:
            errors.append(
                f"Plan tenant_id '{plan.tenant_id}' mismatches "
                f"authenticated scope '{target_tenant_id}'."
            )

        if target_agent_id and plan.agent_id != target_agent_id:
            errors.append(
                f"Plan agent_id '{plan.agent_id}' mismatches target agent '{target_agent_id}'."
            )

        # 2. Steps presence check
        if not plan.steps:
            errors.append("Plan must contain at least one step.")

        step_ids: set[str] = set()
        step_id_to_seq: dict[str, int] = {}
        seq_numbers: list[int] = []

        # 3. Step Uniqueness & Sequence Check
        for idx, step in enumerate(plan.steps, start=1):
            if step.step_id in step_ids:
                errors.append(f"Duplicate step_id '{step.step_id}' found in plan.")
            step_ids.add(step.step_id)
            step_id_to_seq[step.step_id] = step.sequence
            seq_numbers.append(step.sequence)

            if step.sequence != idx:
                errors.append(f"Step '{step.step_id}' sequence {step.sequence} is non-contiguous.")

            if step.action not in SUPPORTED_PLAN_ACTIONS:
                errors.append(f"Step '{step.step_id}' action '{step.action}' is not supported.")

        # 4. Dependency Integrity & Cycle Detection (DAG Check)
        graph: dict[str, list[str]] = {step.step_id: [] for step in plan.steps}

        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Step '{step.step_id}' depends on non-existent step '{dep}'.")
                elif step_id_to_seq.get(dep, 0) >= step.sequence:
                    errors.append(
                        f"Step '{step.step_id}' depends on forward or equal step '{dep}'."
                    )
                else:
                    graph[dep].append(step.step_id)

        # Cycle detection using DFS
        visited: dict[str, int] = {s: 0 for s in step_ids}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(node: str) -> bool:
            visited[node] = 1
            for neighbor in graph.get(node, []):
                if visited.get(neighbor) == 1:
                    return True  # Cycle found!
                if visited.get(neighbor) == 0 and dfs(neighbor):
                    return True
            visited[node] = 2
            return False

        for node in step_ids:
            if visited[node] == 0:
                if dfs(node):
                    errors.append("Circular dependency detected in plan step graph.")
                    break

        # 5. Secret Leakage Scan
        self._scan_for_secrets([s.model_dump(mode="json") for s in plan.steps], "steps", errors)
        self._scan_for_secrets(plan.constraints.model_dump(mode="json"), "constraints", errors)

        # 6. Intent & Execution Eligibility Invariants
        if plan.intent_type == "UNKNOWN":
            for step in plan.steps:
                if step.execution_eligible:
                    errors.append("UNKNOWN intent plan step must not be execution_eligible=True.")

        is_valid = len(errors) == 0
        execution_eligible = (
            is_valid
            and plan.intent_type != "UNKNOWN"
            and any(s.execution_eligible for s in plan.steps)
        )

        logger.info(
            "Plan validation completed",
            extra={
                "plan_id": str(plan.plan_id),
                "is_valid": is_valid,
                "error_count": len(errors),
                "execution_eligible": execution_eligible,
            },
        )

        return PlanValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            execution_eligible=execution_eligible,
            validation_version="1.0.0",
        )
