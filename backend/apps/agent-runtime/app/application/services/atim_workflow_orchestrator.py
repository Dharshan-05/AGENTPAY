"""ATIM Durable Workflow Execution Orchestrator Service (Phase 23 / Group 12)."""

from datetime import datetime
import hashlib
import json
import logging
from typing import Any, Optional
import uuid

from app.application.services.atim_audit_lock_service import ATIMAuditLockService
from app.application.services.atim_compliance_evidence_service import ATIMComplianceEvidenceService
from app.domain.governance.compliance_models import ComplianceEventCategory
from app.domain.governance.workflow_models import (
    WorkflowInstanceRecord,
    WorkflowState,
    WorkflowStepRecord,
    WorkflowStepType,
)
from app.infrastructure.observability.sanitization import TelemetrySanitizer

logger = logging.getLogger("agentpay.atim.workflow")


class ATIMWorkflowOrchestrator:
    """Service managing stateful durable workflow instances, step idempotency, and audit logging."""

    def __init__(
        self,
        audit_lock_service: Optional[ATIMAuditLockService] = None,
        compliance_service: Optional[ATIMComplianceEvidenceService] = None,
    ) -> None:
        self.audit_lock = audit_lock_service or ATIMAuditLockService()
        self.compliance_service = compliance_service or ATIMComplianceEvidenceService(self.audit_lock)
        # In-memory store fallback for fast testing and DB persistence synchronization
        self._instances: dict[uuid.UUID, WorkflowInstanceRecord] = {}
        self._step_history: dict[tuple[uuid.UUID, int], WorkflowStepRecord] = {}

    def compute_payload_hash(self, payload: dict[str, Any]) -> str:
        """Compute SHA-256 fingerprint over step parameters."""
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def start_workflow(
        self,
        tenant_id: uuid.UUID,
        workflow_type: str,
        correlation_id: str,
        total_steps: int = 1,
        agent_id: Optional[uuid.UUID] = None,
    ) -> WorkflowInstanceRecord:
        """Initiate a new durable workflow instance."""
        workflow_id = uuid.uuid4()
        record = WorkflowInstanceRecord(
            id=workflow_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            workflow_type=workflow_type,
            state=WorkflowState.INITIATED,
            current_step_index=0,
            total_steps=total_steps,
            correlation_id=correlation_id,
        )

        sig = self.audit_lock.generate_audit_signature(
            tenant_id=tenant_id,
            request_id=workflow_id,
            record_type="WORKFLOW_INITIATED",
            payload=record.model_dump(mode="json"),
        )
        record.signature = sig.signature

        self._instances[workflow_id] = record
        self.compliance_service.record_evidence(
            tenant_id=tenant_id,
            actor_id=agent_id or tenant_id,
            category=ComplianceEventCategory.EXECUTION_PROPOSAL,
            correlation_id=correlation_id,
            details={"workflow_id": str(workflow_id), "workflow_type": workflow_type, "action": "WORKFLOW_INITIATED"},
            agent_id=agent_id,
        )

        logger.info("Initiated workflow %s (Type: %s) for Tenant %s", workflow_id, workflow_type, tenant_id)
        return record

    def execute_workflow_step(
        self,
        workflow_id: uuid.UUID,
        step_index: int,
        step_type: WorkflowStepType,
        input_params: dict[str, Any],
        handler_result: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, WorkflowStepRecord]:
        """Execute or retrieve step execution record for workflow.

        Returns:
            Tuple (is_replayed: bool, step_record: WorkflowStepRecord)
        """
        instance = self._instances.get(workflow_id)
        if not instance:
            raise KeyError(f"Workflow instance '{workflow_id}' not found.")

        if instance.state in (WorkflowState.COMPLETED, WorkflowState.CANCELLED, WorkflowState.FAILED):
            raise ValueError(f"Cannot execute step on workflow in terminal state '{instance.state.value}'.")

        step_key = (workflow_id, step_index)
        payload_hash = self.compute_payload_hash(input_params)

        existing_step = self._step_history.get(step_key)
        if existing_step:
            if existing_step.payload_hash != payload_hash:
                raise ValueError(f"Step payload hash mismatch for workflow {workflow_id} at step index {step_index}.")
            logger.info("Replayed completed step %d for workflow %s", step_index, workflow_id)
            return True, existing_step

        # Record step execution
        sanitized_input = TelemetrySanitizer.sanitize_dict(input_params)
        sanitized_output = TelemetrySanitizer.sanitize_dict(handler_result) if handler_result else {}

        step_record = WorkflowStepRecord(
            workflow_id=workflow_id,
            step_index=step_index,
            step_type=step_type,
            status="COMPLETED",
            payload_hash=payload_hash,
            input_params=sanitized_input,
            output_result=sanitized_output,
            completed_at=datetime.utcnow(),
        )

        self._step_history[step_key] = step_record
        instance.current_step_index = step_index + 1
        instance.state = WorkflowState.STEP_COMPLETED
        instance.updated_at = datetime.utcnow()

        if instance.current_step_index >= instance.total_steps:
            instance.state = WorkflowState.COMPLETED
            instance.completed_at = datetime.utcnow()

        logger.info("Completed step %d (%s) for workflow %s", step_index, step_type.value, workflow_id)
        return False, step_record

    def cancel_workflow(self, workflow_id: uuid.UUID, reason: str) -> WorkflowInstanceRecord:
        """Cancel an active workflow instance."""
        instance = self._instances.get(workflow_id)
        if not instance:
            raise KeyError(f"Workflow instance '{workflow_id}' not found.")

        instance.state = WorkflowState.CANCELLED
        instance.updated_at = datetime.utcnow()
        instance.completed_at = datetime.utcnow()

        logger.warning("Cancelled workflow %s: %s", workflow_id, reason)
        return instance

    def get_workflow_instance(self, workflow_id: uuid.UUID) -> Optional[WorkflowInstanceRecord]:
        """Retrieve workflow instance by ID."""
        return self._instances.get(workflow_id)
