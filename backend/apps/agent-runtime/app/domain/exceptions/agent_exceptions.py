"""Agent domain exception abstractions for AGENTPAY (Phase 119–135)."""

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class AgentNotFoundError(AgentPayError):
    """Domain exception raised when an agent is not found within tenant scope (IDOR-safe)."""

    def __init__(self, message: str = "Agent not found or access denied.") -> None:
        """Initialize AgentNotFoundError with safe 404 message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentAlreadyExistsError(AgentPayError):
    """Domain exception raised when creating an agent with duplicate tenant-scoped slug."""

    def __init__(self, message: str = "Agent with this slug already exists within tenant.") -> None:
        """Initialize AgentAlreadyExistsError with conflict message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentIdentityNotFoundError(AgentPayError):
    """Domain exception raised when an agent identity is not found within tenant scope."""

    def __init__(self, message: str = "Agent identity not found or access denied.") -> None:
        """Initialize AgentIdentityNotFoundError with safe 404 message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentIdentityAlreadyExistsError(AgentPayError):
    """Domain exception raised when creating duplicate identity for an agent."""

    def __init__(self, message: str = "Identity already exists for this agent.") -> None:
        """Initialize AgentIdentityAlreadyExistsError with conflict message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentCredentialError(AgentPayError):
    """Domain exception raised for general agent credential failures."""

    def __init__(self, message: str = "Agent credential error.") -> None:
        """Initialize AgentCredentialError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentCredentialNotFoundError(AgentPayError):
    """Domain exception raised when an agent credential is not found within tenant scope."""

    def __init__(self, message: str = "Agent credential not found or access denied.") -> None:
        """Initialize AgentCredentialNotFoundError with safe 404 message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentCredentialAlreadyExistsError(AgentPayError):
    """Domain exception raised when a duplicate agent credential is provided."""

    def __init__(self, message: str = "Agent credential already exists.") -> None:
        """Initialize AgentCredentialAlreadyExistsError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class InvalidAgentLifecycleTransitionError(AgentPayError):
    """Domain exception raised when an invalid agent status transition is attempted."""

    def __init__(self, message: str = "Invalid agent lifecycle state transition.") -> None:
        """Initialize InvalidAgentLifecycleTransitionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentActivationError(AgentPayError):
    """Domain exception raised when agent activation business rules fail."""

    def __init__(self, message: str = "Agent activation failed.") -> None:
        """Initialize AgentActivationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentAlreadyActiveError(AgentPayError):
    """Domain exception raised when activating an agent that is already active."""

    def __init__(self, message: str = "Agent is already active.") -> None:
        """Initialize AgentAlreadyActiveError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentSuspensionError(AgentPayError):
    """Domain exception raised for agent suspension business logic failures."""

    def __init__(self, message: str = "Agent suspension failed.") -> None:
        """Initialize AgentSuspensionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentAlreadySuspendedError(AgentPayError):
    """Domain exception raised when suspending an agent that is already suspended."""

    def __init__(self, message: str = "Agent is already suspended.") -> None:
        """Initialize AgentAlreadySuspendedError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentRevocationError(AgentPayError):
    """Domain exception raised for agent revocation business logic failures."""

    def __init__(self, message: str = "Agent revocation failed.") -> None:
        """Initialize AgentRevocationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentAlreadyRevokedError(AgentPayError):
    """Domain exception raised when revoking an agent that is already deactivated/revoked."""

    def __init__(self, message: str = "Agent is already deactivated/revoked.") -> None:
        """Initialize AgentAlreadyRevokedError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentSessionError(AgentPayError):
    """Domain exception raised for general agent session errors."""

    def __init__(self, message: str = "Agent session error.") -> None:
        """Initialize AgentSessionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentSessionNotFoundError(AgentPayError):
    """Domain exception raised when an agent session is not found within tenant scope."""

    def __init__(self, message: str = "Agent session not found or access denied.") -> None:
        """Initialize AgentSessionNotFoundError with safe 404 message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentSessionAlreadyRevokedError(AgentPayError):
    """Domain exception raised when revoking a session that is already revoked."""

    def __init__(self, message: str = "Agent session is already revoked.") -> None:
        """Initialize AgentSessionAlreadyRevokedError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentSessionValidationError(AgentPayError):
    """Domain exception raised when an agent session validation fails."""

    def __init__(self, message: str = "Agent session validation failed.") -> None:
        """Initialize AgentSessionValidationError."""
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
        )


class AgentSessionCreationError(AgentPayError):
    """Domain exception raised when creating an agent session fails."""

    def __init__(self, message: str = "Agent session creation failed.") -> None:
        """Initialize AgentSessionCreationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentPermissionError(AgentPayError):
    """Domain exception raised for agent permission management failures."""

    def __init__(self, message: str = "Agent permission error.") -> None:
        """Initialize AgentPermissionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentPermissionNotFoundError(AgentPayError):
    """Domain exception raised when an assigned agent permission is not found."""

    def __init__(self, message: str = "Agent permission assignment not found.") -> None:
        """Initialize AgentPermissionNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentPermissionAlreadyAssignedError(AgentPayError):
    """Domain exception raised when assigning a permission already assigned to agent."""

    def __init__(self, message: str = "Permission is already assigned to this agent.") -> None:
        """Initialize AgentPermissionAlreadyAssignedError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentPermissionAssignmentError(AgentPayError):
    """Domain exception raised when an invalid permission assignment is attempted."""

    def __init__(self, message: str = "Invalid agent permission assignment.") -> None:
        """Initialize AgentPermissionAssignmentError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentRoleError(AgentPayError):
    """Domain exception raised for agent role management failures."""

    def __init__(self, message: str = "Agent role error.") -> None:
        """Initialize AgentRoleError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentRoleNotFoundError(AgentPayError):
    """Domain exception raised when an assigned agent role is not found."""

    def __init__(self, message: str = "Agent role assignment not found.") -> None:
        """Initialize AgentRoleNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentRoleAlreadyAssignedError(AgentPayError):
    """Domain exception raised when assigning a role already assigned to agent."""

    def __init__(self, message: str = "Role is already assigned to this agent.") -> None:
        """Initialize AgentRoleAlreadyAssignedError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class AgentRoleAssignmentError(AgentPayError):
    """Domain exception raised when an invalid role assignment is attempted."""

    def __init__(self, message: str = "Invalid agent role assignment.") -> None:
        """Initialize AgentRoleAssignmentError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentStatusError(AgentPayError):
    """Domain exception raised for general agent status management failures."""

    def __init__(self, message: str = "Agent status error.") -> None:
        """Initialize AgentStatusError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentStatusTransitionError(AgentPayError):
    """Domain exception raised when an invalid agent status update is requested."""

    def __init__(self, message: str = "Invalid agent status transition.") -> None:
        """Initialize AgentStatusTransitionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentMetadataError(AgentPayError):
    """Domain exception raised for general agent metadata management errors."""

    def __init__(self, message: str = "Agent metadata error.") -> None:
        """Initialize AgentMetadataError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentMetadataNotFoundError(AgentPayError):
    """Domain exception raised when metadata is not found for an agent within tenant scope."""

    def __init__(self, message: str = "Agent metadata not found or access denied.") -> None:
        """Initialize AgentMetadataNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentAuditError(AgentPayError):
    """Domain exception raised for general agent audit trail failures."""

    def __init__(self, message: str = "Agent audit error.") -> None:
        """Initialize AgentAuditError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentSecurityEventError(AgentPayError):
    """Domain exception raised for general agent security event failures."""

    def __init__(self, message: str = "Agent security event error.") -> None:
        """Initialize AgentSecurityEventError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentTrustError(AgentPayError):
    """Domain exception raised for general agent trust data errors."""

    def __init__(self, message: str = "Agent trust data error.") -> None:
        """Initialize AgentTrustError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentTrustNotFoundError(AgentPayError):
    """Domain exception raised when trust data is not found for an agent."""

    def __init__(self, message: str = "Agent trust data not found or access denied.") -> None:
        """Initialize AgentTrustNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class InvalidAgentTrustScoreError(AgentPayError):
    """Domain exception raised when an invalid trust score value is provided."""

    def __init__(self, message: str = "Trust score must be between 0.00 and 100.00.") -> None:
        """Initialize InvalidAgentTrustScoreError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentBehaviourDeviationError(AgentPayError):
    """Domain exception raised for failures during behaviour deviation calculation."""

    def __init__(self, message: str = "Agent behaviour deviation calculation error.") -> None:
        """Initialize AgentBehaviourDeviationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentVelocityDetectionError(AgentPayError):
    """Domain exception raised for failures during velocity detection calculation."""

    def __init__(self, message: str = "Agent velocity detection error.") -> None:
        """Initialize AgentVelocityDetectionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentMerchantBehaviourError(AgentPayError):
    """Domain exception raised for failures during merchant behaviour analysis."""

    def __init__(self, message: str = "Agent merchant behaviour analysis error.") -> None:
        """Initialize AgentMerchantBehaviourError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class AgentCategoryBehaviourError(AgentPayError):
    """Domain exception raised for failures during category behaviour analysis."""

    def __init__(self, message: str = "Agent category behaviour analysis error.") -> None:
        """Initialize AgentCategoryBehaviourError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class IntentExtractionError(AgentPayError):
    """Domain exception raised for failures during intent extraction."""

    def __init__(self, message: str = "Intent extraction error.") -> None:
        """Initialize IntentExtractionError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class IntentClassificationError(AgentPayError):
    """Domain exception raised for failures during intent classification."""

    def __init__(self, message: str = "Intent classification error.") -> None:
        """Initialize IntentClassificationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class StructuredIntentError(AgentPayError):
    """Domain exception raised for structured intent schema validation failures."""

    def __init__(self, message: str = "Structured intent validation error.") -> None:
        """Initialize StructuredIntentError."""
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
        )


class IntentValidationError(AgentPayError):
    """Domain exception raised for intent validation failures (Phase 143)."""

    def __init__(self, message: str = "Intent validation failed.") -> None:
        """Initialize IntentValidationError."""
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
        )


class IntentNormalizationError(AgentPayError):
    """Domain exception raised for intent normalization failures (Phase 144)."""

    def __init__(self, message: str = "Intent normalization failed.") -> None:
        """Initialize IntentNormalizationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class IntentStorageError(AgentPayError):
    """Domain exception raised for intent storage failures (Phase 145)."""

    def __init__(self, message: str = "Intent storage failed.") -> None:
        """Initialize IntentStorageError."""
        super().__init__(
            message=message,
            code=ErrorCode.INFRASTRUCTURE_ERROR,
        )


class IntentNotFoundError(AgentPayError):
    """Domain exception raised when a requested stored intent is missing (Phase 145)."""

    def __init__(self, message: str = "Stored intent not found.") -> None:
        """Initialize IntentNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentPlanningError(AgentPayError):
    """Base domain exception raised for planning engine failures (Phase 146)."""

    def __init__(self, message: str = "Agent planning failed.") -> None:
        """Initialize AgentPlanningError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
        )


class PlanGenerationError(AgentPlanningError):
    """Domain exception raised when plan generation fails (Phase 147)."""

    def __init__(self, message: str = "Plan generation failed.") -> None:
        """Initialize PlanGenerationError."""
        super().__init__(message=message)


class PlanValidationError(AgentPlanningError):
    """Domain exception raised when plan validation fails (Phase 148)."""

    def __init__(self, message: str = "Plan validation failed.") -> None:
        """Initialize PlanValidationError."""
        super().__init__(message=message)


class InvalidPlanError(PlanValidationError):
    """Domain exception raised when a plan is structurally invalid (Phase 148)."""

    def __init__(self, message: str = "Plan representation is invalid.") -> None:
        """Initialize InvalidPlanError."""
        super().__init__(message=message)


class PlanDependencyError(PlanValidationError):
    """Domain exception raised when step dependency validation fails (Phase 148)."""

    def __init__(self, message: str = "Plan step dependencies are invalid or cyclic.") -> None:
        """Initialize PlanDependencyError."""
        super().__init__(message=message)


class UnsupportedPlanActionError(PlanValidationError):
    """Domain exception raised when a plan step contains an unsupported action (Phase 148)."""

    def __init__(self, message: str = "Plan contains unsupported action.") -> None:
        """Initialize UnsupportedPlanActionError."""
        super().__init__(message=message)


class PlanNotFoundError(AgentPayError):
    """Domain exception raised when a requested plan is missing or cross-tenant (Phase 146-148)."""

    def __init__(self, message: str = "Plan not found or access denied.") -> None:
        """Initialize PlanNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentOrchestrationError(AgentPayError):
    """Base domain exception raised for agent orchestration failures (Phase 149)."""

    def __init__(
        self,
        message: str = "Agent orchestration failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentOrchestrationError."""
        super().__init__(
            message=message,
            code=code,
        )


class OrchestrationValidationError(AgentOrchestrationError):
    """Domain exception raised when orchestration validation fails (Phase 149)."""

    def __init__(self, message: str = "Orchestration validation failed.") -> None:
        """Initialize OrchestrationValidationError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class OrchestrationRejectedError(AgentOrchestrationError):
    """Domain exception raised when an orchestration decision is rejected (Phase 149)."""

    def __init__(self, message: str = "Orchestration request rejected.") -> None:
        """Initialize OrchestrationRejectedError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class OrchestrationBlockedError(AgentOrchestrationError):
    """Domain exception raised when an orchestration request is blocked (Phase 149)."""

    def __init__(self, message: str = "Orchestration request blocked.") -> None:
        """Initialize OrchestrationBlockedError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class OrchestrationNotFoundError(AgentPayError):
    """Domain exception raised when orchestration is missing or cross-tenant (Phase 149)."""

    def __init__(self, message: str = "Orchestration record not found.") -> None:
        """Initialize OrchestrationNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class AgentStateError(AgentPayError):
    """Base domain exception raised for agent runtime state failures (Phase 150)."""

    def __init__(
        self,
        message: str = "Agent state operation failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentStateError."""
        super().__init__(
            message=message,
            code=code,
        )


class InvalidAgentStateTransitionError(AgentStateError):
    """Domain exception raised when an invalid runtime state transition is attempted (Phase 150)."""

    def __init__(self, message: str = "Invalid agent state transition.") -> None:
        """Initialize InvalidAgentStateTransitionError."""
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
        )


class AgentExecutionError(AgentPayError):
    """Base domain exception raised for agent execution loop failures (Phase 151)."""

    def __init__(
        self,
        message: str = "Agent execution failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentExecutionError."""
        super().__init__(
            message=message,
            code=code,
        )


class ExecutionValidationError(AgentExecutionError):
    """Domain exception raised when execution validation fails (Phase 151)."""

    def __init__(self, message: str = "Execution validation failed.") -> None:
        """Initialize ExecutionValidationError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class ExecutionNotFoundError(AgentPayError):
    """Domain exception raised when an execution record is missing or cross-tenant (Phase 151)."""

    def __init__(self, message: str = "Execution not found or access denied.") -> None:
        """Initialize ExecutionNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class ExecutionBlockedError(AgentExecutionError):
    """Domain exception raised when execution is blocked (Phase 151)."""

    def __init__(self, message: str = "Execution blocked.") -> None:
        """Initialize ExecutionBlockedError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class ExecutionCancelledError(AgentExecutionError):
    """Domain exception raised when an execution is cancelled (Phase 151)."""

    def __init__(self, message: str = "Execution cancelled.") -> None:
        """Initialize ExecutionCancelledError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class ExecutionStepError(AgentExecutionError):
    """Domain exception raised when an execution step fails (Phase 151)."""

    def __init__(self, message: str = "Execution step failed.") -> None:
        """Initialize ExecutionStepError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class ExecutionRetryLimitExceededError(AgentExecutionError):
    """Domain exception raised when step retries exceed maximum limit (Phase 151)."""

    def __init__(self, message: str = "Execution step retries exceeded limit.") -> None:
        """Initialize ExecutionRetryLimitExceededError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class ExecutionPolicyViolationError(AgentExecutionError):
    """Domain exception raised on policy or security violations during execution (Phase 151)."""

    def __init__(self, message: str = "Execution policy violation.") -> None:
        """Initialize ExecutionPolicyViolationError."""
        super().__init__(message=message, code=ErrorCode.FORBIDDEN)


class AgentContextError(AgentPayError):
    """Base domain exception raised for context management failures (Phase 152)."""

    def __init__(
        self,
        message: str = "Agent context operation failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentContextError."""
        super().__init__(message=message, code=code)


class ContextBudgetExceededError(AgentContextError):
    """Domain exception raised when context assembly exceeds strict token budget (Phase 152)."""

    def __init__(self, message: str = "Context token budget exceeded.") -> None:
        """Initialize ContextBudgetExceededError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class ContextValidationError(AgentContextError):
    """Domain exception raised when context payload validation fails (Phase 152)."""

    def __init__(self, message: str = "Context validation failed.") -> None:
        """Initialize ContextValidationError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class AgentMemoryError(AgentPayError):
    """Base domain exception raised for agent memory operations (Phase 153/154)."""

    def __init__(
        self,
        message: str = "Agent memory operation failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentMemoryError."""
        super().__init__(message=message, code=code)


class MemoryNotFoundError(AgentPayError):
    """Domain exception raised when a requested memory record is missing (Phase 153/154)."""

    def __init__(self, message: str = "Memory record not found or access denied.") -> None:
        """Initialize MemoryNotFoundError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_NOT_FOUND)


class MemoryValidationError(AgentMemoryError):
    """Domain exception raised when memory validation fails (Phase 153/154)."""

    def __init__(self, message: str = "Memory record validation failed.") -> None:
        """Initialize MemoryValidationError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class MemoryQuotaExceededError(AgentMemoryError):
    """Domain exception raised when session/task memory quota is exceeded (Phase 154)."""

    def __init__(self, message: str = "Short-term memory quota exceeded.") -> None:
        """Initialize MemoryQuotaExceededError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class MemoryAccessDeniedError(AgentMemoryError):
    """Domain exception raised on cross-tenant or unauthorized memory access (Phase 153/154)."""

    def __init__(self, message: str = "Memory access denied.") -> None:
        """Initialize MemoryAccessDeniedError."""
        super().__init__(message=message, code=ErrorCode.FORBIDDEN)


# ============================================================================
# PHASE 161 — AGENT TRANSACTION ORCHESTRATION EXCEPTIONS
# ============================================================================


class AgentTransactionOrchestrationError(AgentPayError):
    """Base exception for agent transaction orchestration failures (Phase 161)."""

    def __init__(
        self,
        message: str = "Agent transaction orchestration failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize AgentTransactionOrchestrationError."""
        super().__init__(message=message, code=code)


class WorkflowExecutionError(AgentTransactionOrchestrationError):
    """Raised when agent transaction workflow execution fails (Phase 161)."""

    def __init__(self, message: str = "Workflow execution failed.") -> None:
        """Initialize WorkflowExecutionError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class WorkflowCancelledError(AgentTransactionOrchestrationError):
    """Raised when an orchestrated workflow is cancelled (Phase 161)."""

    def __init__(self, message: str = "Workflow has been cancelled.") -> None:
        """Initialize WorkflowCancelledError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class WorkflowExpiredError(AgentTransactionOrchestrationError):
    """Raised when an orchestrated workflow times out or expires (Phase 161)."""

    def __init__(self, message: str = "Workflow execution has expired.") -> None:
        """Initialize WorkflowExpiredError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


# ============================================================================
# PHASE 162 — HUMAN APPROVAL WORKFLOW EXCEPTIONS
# ============================================================================


class HumanApprovalError(AgentPayError):
    """Base exception for human approval workflow operations (Phase 162)."""

    def __init__(
        self,
        message: str = "Human approval operation failed.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize HumanApprovalError."""
        super().__init__(message=message, code=code)


class SelfApprovalForbiddenError(HumanApprovalError):
    """Raised when an agent or requesting user attempts to self-approve a restricted action (Phase 162)."""  # noqa: E501

    def __init__(self, message: str = "Self-approval of restricted actions is forbidden.") -> None:
        """Initialize SelfApprovalForbiddenError."""
        super().__init__(message=message, code=ErrorCode.FORBIDDEN)


class ApprovalRequiredError(HumanApprovalError):
    """Raised when a sensitive transaction requires human approval before proceeding (Phase 162)."""

    def __init__(self, message: str = "Human approval is required before execution.") -> None:
        """Initialize ApprovalRequiredError."""
        super().__init__(message=message, code=ErrorCode.FORBIDDEN)


class ApprovalExpiredError(HumanApprovalError):
    """Raised when an approval request has expired (Phase 162)."""

    def __init__(self, message: str = "Approval request has expired.") -> None:
        """Initialize ApprovalExpiredError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


# ============================================================================
# PHASE 163 — AGENT EXECUTION RELIABILITY EXCEPTIONS
# ============================================================================


class ExecutionReliabilityError(AgentPayError):
    """Base exception for agent execution reliability failures (Phase 163)."""

    def __init__(
        self,
        message: str = "Agent execution reliability failure.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize ExecutionReliabilityError."""
        super().__init__(message=message, code=code)


class CircuitBreakerOpenError(ExecutionReliabilityError):
    """Raised when execution is rejected due to an open circuit breaker (Phase 163)."""

    def __init__(self, message: str = "Circuit breaker is OPEN. Requests blocked.") -> None:
        """Initialize CircuitBreakerOpenError."""
        super().__init__(message=message, code=ErrorCode.SERVICE_UNAVAILABLE)


class NonRetryableExecutionError(ExecutionReliabilityError):
    """Raised when execution fails with a non-retryable error (Phase 163)."""

    def __init__(self, message: str = "Execution failed with non-retryable error.") -> None:
        """Initialize NonRetryableExecutionError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


class ReconciliationRequiredError(ExecutionReliabilityError):
    """Raised when execution requires manual or automated financial reconciliation (Phase 163)."""

    def __init__(self, message: str = "Execution requires financial reconciliation.") -> None:
        """Initialize ReconciliationRequiredError."""
        super().__init__(message=message, code=ErrorCode.DOMAIN_ERROR)


# ============================================================================
# PHASE 156 / 157 — TOOL CALLING FRAMEWORK & REGISTRY EXCEPTIONS
# ============================================================================


class ToolError(AgentPayError):
    """Base exception for tool registration and execution failures (Phase 156/157)."""

    def __init__(
        self,
        message: str = "Tool operation failure.",
        code: ErrorCode = ErrorCode.DOMAIN_ERROR,
    ) -> None:
        """Initialize ToolError."""
        super().__init__(message=message, code=code)


class ToolNotFoundError(ToolError):
    """Raised when requested tool is not found in registry (Phase 156/157)."""

    def __init__(self, message: str = "Requested tool was not found in registry.") -> None:
        """Initialize ToolNotFoundError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_NOT_FOUND)


class ToolValidationError(ToolError):
    """Raised when tool input or argument validation fails (Phase 156)."""

    def __init__(self, message: str = "Tool argument validation failed.") -> None:
        """Initialize ToolValidationError."""
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class ToolExecutionError(ToolError):
    """Raised when tool execution fails (Phase 156)."""

    def __init__(self, message: str = "Tool execution failed.") -> None:
        """Initialize ToolExecutionError."""
        super().__init__(message=message, code=ErrorCode.APPLICATION_ERROR)


class ToolTimeoutError(ToolError):
    """Raised when tool execution exceeds time limit (Phase 156)."""

    def __init__(self, message: str = "Tool execution timed out.") -> None:
        """Initialize ToolTimeoutError."""
        super().__init__(message=message, code=ErrorCode.SERVICE_UNAVAILABLE)


class ToolPermissionDeniedError(ToolError):
    """Raised when agent is not authorized to execute tool (Phase 156/158)."""

    def __init__(self, message: str = "Permission denied for tool execution.") -> None:
        """Initialize ToolPermissionDeniedError."""
        super().__init__(message=message, code=ErrorCode.FORBIDDEN)


class ToolDisabledError(ToolError):
    """Raised when execution of a disabled or deprecated tool is requested (Phase 157)."""

    def __init__(self, message: str = "Tool is disabled or deprecated.") -> None:
        """Initialize ToolDisabledError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class ToolAlreadyExistsError(ToolError):
    """Raised when attempting to register a duplicate tool ID and version (Phase 157)."""

    def __init__(self, message: str = "Tool with this ID and version already exists.") -> None:
        """Initialize ToolAlreadyExistsError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class ToolVersionMismatchError(ToolError):
    """Raised when requested tool version is not available (Phase 157)."""

    def __init__(self, message: str = "Tool version mismatch.") -> None:
        """Initialize ToolVersionMismatchError."""
        super().__init__(message=message, code=ErrorCode.RESOURCE_NOT_FOUND)


# ---------------------------------------------------------------------------
# Commerce Engine — Merchant & Product Domain Exceptions (Phase 164–165)
# ---------------------------------------------------------------------------
class MerchantNotFoundError(AgentPayError):
    """Raised when a merchant is not found within tenant scope (IDOR-safe)."""

    def __init__(self, message: str = "Merchant not found or access denied.") -> None:
        super().__init__(message=message, code=ErrorCode.RESOURCE_NOT_FOUND)


class MerchantAlreadyExistsError(AgentPayError):
    """Raised when creating a merchant with duplicate tenant-scoped slug."""

    def __init__(
        self, message: str = "Merchant with this slug already exists within tenant."
    ) -> None:  # noqa: E501
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class MerchantValidationError(AgentPayError):
    """Raised when merchant input validation fails."""

    def __init__(self, message: str = "Merchant validation error.") -> None:
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)


class ProductNotFoundError(AgentPayError):
    """Raised when a product is not found within tenant scope (IDOR-safe)."""

    def __init__(self, message: str = "Product not found or access denied.") -> None:
        super().__init__(message=message, code=ErrorCode.RESOURCE_NOT_FOUND)


class ProductAlreadyExistsError(AgentPayError):
    """Raised when creating a product with duplicate SKU for merchant."""

    def __init__(self, message: str = "Product with this SKU already exists for merchant.") -> None:
        super().__init__(message=message, code=ErrorCode.RESOURCE_CONFLICT)


class ProductValidationError(AgentPayError):
    """Raised when product input validation fails."""

    def __init__(self, message: str = "Product validation error.") -> None:
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR)
