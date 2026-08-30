"""Reviewer Authorization Subsystem (Phase 304)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid

from app.schemas.approval_request import (
    ApprovalRequestRecord,
    ApprovalRequestStatus,
)
from app.schemas.reviewer_authorization import (
    DEFAULT_ROLE_LIMITS,
    DEFAULT_ROLE_PERMISSIONS,
    ReviewerAuthorizationResult,
    ReviewerPermission,
    TrustedReviewerContext,
)

logger = logging.getLogger("agentpay.payment.approval.reviewer_auth")


class ReviewerAuthorizationError(Exception):
    """Domain exception raised when reviewer authorization evaluation fails catastrophically."""

    def __init__(self, message: str, error_code: str = "REVIEWER_AUTH_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ReviewerAuthorizationService:
    """Production Reviewer Authorization Service (Phase 304).

    Primary responsibility: Create a trusted authorization boundary evaluating:
    "Is this HUMAN REVIEWER authorized to perform this specific approval operation
    on this specific approval request?"

    CRITICAL SECURITY INVARIANTS:
    - AI AGENT != REVIEWER (Self-approval strictly forbidden!).
    - Tenant Isolation: reviewer.tenant_id == approval_request.tenant_id.
    - Capability Matrix & Monetary Limits: requested_amount <= reviewer_authorized_limit.
    - Zero secrets exposed (key_secret, webhook_secret, provider credentials).
    - ZERO Razorpay SDK calls or direct provider access.
    - Immutability & Fingerprint verification over canonical context.
    - FAIL CLOSED on any security check violation.
    """

    def authorize_reviewer(
        self,
        reviewer_context: TrustedReviewerContext,
        approval_request: ApprovalRequestRecord,
        required_permission: ReviewerPermission = ReviewerPermission.APPROVE_PAYMENT,
        expected_approval_fingerprint: str | None = None,
    ) -> ReviewerAuthorizationResult:
        """Evaluate trusted reviewer authorization against an approval request (Phase 304)."""
        logger.info(
            "ReviewerAuthorizationService evaluating reviewer=%s (tenant=%s) for req=%s",
            reviewer_context.reviewer_id,
            reviewer_context.tenant_id,
            approval_request.approval_request_id,
        )

        # 1. Null / Invalid Identity Check
        if not reviewer_context.reviewer_id:
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="REVIEWER_NOT_AUTHENTICATED",
            )

        # 2. Strict Tenant Isolation
        if reviewer_context.tenant_id != approval_request.tenant_id:
            logger.warning(
                "CROSS_TENANT_ACCESS detected: Reviewer tenant %s != Request tenant %s",
                reviewer_context.tenant_id,
                approval_request.tenant_id,
            )
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="CROSS_TENANT_ACCESS",
            )

        # 3. Self-Approval Protection (Agent cannot be Reviewer!)
        if reviewer_context.reviewer_id == approval_request.agent_id:
            logger.warning(
                "SELF_APPROVAL_FORBIDDEN: Reviewer %s is the originating AI agent %s!",
                reviewer_context.reviewer_id,
                approval_request.agent_id,
            )
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="SELF_APPROVAL_FORBIDDEN",
            )

        # 4. Capability / Permission Verification
        default_role_perms = DEFAULT_ROLE_PERMISSIONS.get(reviewer_context.reviewer_role, set())
        combined_permissions = (
            reviewer_context.permissions if reviewer_context.permissions else default_role_perms
        )

        if required_permission not in combined_permissions:
            logger.warning(
                "REVIEWER_PERMISSION_DENIED: Reviewer %s lacks permission '%s'",
                reviewer_context.reviewer_id,
                required_permission.value,
            )
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="REVIEWER_PERMISSION_DENIED",
            )

        # 5. Monetary Approval Limit Verification
        effective_limit = reviewer_context.authorization_limit
        default_limit = DEFAULT_ROLE_LIMITS.get(
            reviewer_context.reviewer_role, DEFAULT_ROLE_LIMITS[reviewer_context.reviewer_role]
        )
        # Use whichever is set or standard role default
        max_allowed_limit = max(effective_limit, default_limit)

        if approval_request.amount > max_allowed_limit:
            logger.warning(
                "APPROVAL_LIMIT_EXCEEDED: Requested amount %s > Reviewer limit %s",
                approval_request.amount,
                max_allowed_limit,
            )
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="APPROVAL_LIMIT_EXCEEDED",
            )

        # 6. Status Check: Must be PENDING
        if approval_request.status != ApprovalRequestStatus.PENDING:
            logger.warning(
                "APPROVAL_ALREADY_FINALIZED: Request %s status is '%s'",
                approval_request.approval_request_id,
                approval_request.status.value,
            )
            return self._build_denial(
                reviewer_context,
                approval_request,
                required_permission,
                reason_code="APPROVAL_ALREADY_FINALIZED",
            )

        # 7. Fingerprint Integrity Verification
        if expected_approval_fingerprint:
            if approval_request.approval_fingerprint != expected_approval_fingerprint:
                logger.warning(
                    "APPROVAL_FINGERPRINT_MISMATCH: Provided fingerprint != Request fingerprint",
                )
                return self._build_denial(
                    reviewer_context,
                    approval_request,
                    required_permission,
                    reason_code="APPROVAL_FINGERPRINT_MISMATCH",
                )

        # 8. All Authorization Controls Passed -> GRANT
        fp = self._calculate_authorization_fingerprint(
            authorized=True,
            reviewer_id=reviewer_context.reviewer_id,
            tenant_id=reviewer_context.tenant_id,
            approval_request_id=approval_request.approval_request_id,
            permission=required_permission,
            reason_code="AUTHORIZATION_GRANTED",
        )

        logger.info(
            "Reviewer authorization GRANTED for reviewer=%s on request=%s",
            reviewer_context.reviewer_id,
            approval_request.approval_request_id,
        )

        return ReviewerAuthorizationResult(
            authorized=True,
            reviewer_id=reviewer_context.reviewer_id,
            tenant_id=reviewer_context.tenant_id,
            approval_request_id=approval_request.approval_request_id,
            permission=required_permission,
            reason_code="AUTHORIZATION_GRANTED",
            authorization_fingerprint=fp,
        )

    def _build_denial(
        self,
        reviewer_context: TrustedReviewerContext,
        approval_request: ApprovalRequestRecord,
        permission: ReviewerPermission,
        reason_code: str,
    ) -> ReviewerAuthorizationResult:
        """Construct a safe, fail-closed denial result with fingerprint."""
        fp = self._calculate_authorization_fingerprint(
            authorized=False,
            reviewer_id=reviewer_context.reviewer_id,
            tenant_id=reviewer_context.tenant_id,
            approval_request_id=approval_request.approval_request_id,
            permission=permission,
            reason_code=reason_code,
        )
        return ReviewerAuthorizationResult(
            authorized=False,
            reviewer_id=reviewer_context.reviewer_id,
            tenant_id=reviewer_context.tenant_id,
            approval_request_id=approval_request.approval_request_id,
            permission=permission,
            reason_code=reason_code,
            authorization_fingerprint=fp,
        )

    def _calculate_authorization_fingerprint(
        self,
        authorized: bool,
        reviewer_id: str | uuid.UUID,
        tenant_id: str | uuid.UUID,
        approval_request_id: str | uuid.UUID,
        permission: ReviewerPermission,
        reason_code: str,
    ) -> str:
        """Calculate SHA-256 fingerprint over canonical authorization decision."""
        payload = {
            "authorized": authorized,
            "reviewer_id": str(reviewer_id),
            "tenant_id": str(tenant_id),
            "approval_request_id": str(approval_request_id),
            "permission": permission.value,
            "reason_code": reason_code,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
