"""Review Queue Backend Subsystem (Phase 303)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

from app.payment.approval.approval_request_service import ApprovalRequestService
from app.schemas.approval_request import (
    ApprovalRequestPriority,
    ApprovalRequestRecord,
)
from app.schemas.review_queue import (
    ReviewQueueItem,
    ReviewQueueQuery,
    ReviewQueueResult,
)

logger = logging.getLogger("agentpay.payment.approval.queue")

PRIORITY_ORDER = {
    ApprovalRequestPriority.CRITICAL: 4,
    ApprovalRequestPriority.HIGH: 3,
    ApprovalRequestPriority.MEDIUM: 2,
    ApprovalRequestPriority.LOW: 1,
}


class ReviewQueueServiceError(Exception):
    """Domain exception raised when review queue query operations fail."""

    def __init__(self, message: str, error_code: str = "REVIEW_QUEUE_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ReviewQueueService:
    """Production Review Queue Service (Phase 303).

    Primary responsibility: Expose pending approval requests to authorized review interfaces
    with strict multi-tenant isolation, controlled filtering, deterministic ordering, and
    keyset pagination.

    Deterministic Ordering:
    1. priority DESC (CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1)
    2. created_at ASC
    3. approval_request_id ASC

    CRITICAL SECURITY INVARIANTS (Group 18 Boundary):
    - NO payment approvals, rejections, or executions.
    - NO reviewer authorization or decision mutation.
    - NO direct provider or Razorpay SDK calls.
    - ZERO secret leakage (key_secret, webhook_secret, credentials).
    """

    def __init__(self, request_service: ApprovalRequestService) -> None:
        self.request_service = request_service

    def query_queue(self, query: ReviewQueueQuery) -> ReviewQueueResult:
        """Query review queue using tenant context and keyset pagination (Phase 303)."""
        logger.info(
            "ReviewQueueService querying queue for tenant=%s (status=%s, page_size=%s)",
            query.tenant_id,
            query.status.value if query.status else "ALL",
            query.page_size,
        )

        # 1. Fetch internal requests and enforce Strict Tenant Isolation
        all_records = self.request_service.list_all_requests_internal()
        tenant_records = [r for r in all_records if r.tenant_id == query.tenant_id]

        # 2. Apply Controlled Filters
        filtered = self._apply_filters(tenant_records, query)

        # 3. Apply Deterministic Sorting
        # priority DESC, created_at ASC, approval_request_id ASC
        sorted_records = sorted(
            filtered,
            key=lambda r: (
                -PRIORITY_ORDER.get(r.priority, 0),
                r.created_at,
                str(r.approval_request_id),
            ),
        )

        total_count = len(sorted_records)

        # 4. Keyset Pagination Application
        paginated_records = self._apply_keyset_pagination(sorted_records, query)

        # 5. Build Safe ReviewQueueItems (Excludes credentials/secrets)
        items = [
            ReviewQueueItem(
                approval_request_id=r.approval_request_id,
                tenant_id=r.tenant_id,
                agent_id=r.agent_id,
                transaction_id=r.transaction_id,
                order_id=r.order_id,
                payment_id=r.payment_id,
                amount=r.amount,
                currency=r.currency,
                operation=r.operation,
                status=r.status,
                risk_score=r.risk_score,
                priority=r.priority,
                created_at=r.created_at,
                expires_at=r.expires_at,
            )
            for r in paginated_records
        ]

        # 6. Compute Next Cursor
        next_cursor_created_at: Any = None
        next_cursor_id: Any = None

        if len(paginated_records) == query.page_size:
            # Check if there are remaining items after this page
            last_item = paginated_records[-1]
            last_index = sorted_records.index(last_item)
            if last_index + 1 < len(sorted_records):
                next_cursor_created_at = last_item.created_at
                next_cursor_id = last_item.approval_request_id

        # 7. Compute Deterministic Query Fingerprint
        fp = self.calculate_query_fingerprint(
            tenant_id=query.tenant_id,
            total_count=total_count,
            page_size=query.page_size,
            items=items,
        )

        return ReviewQueueResult(
            items=items,
            total_count=total_count,
            page_size=query.page_size,
            next_cursor_created_at=next_cursor_created_at,
            next_cursor_id=next_cursor_id,
            query_fingerprint=fp,
        )

    def _apply_filters(
        self, records: list[ApprovalRequestRecord], query: ReviewQueueQuery
    ) -> list[ApprovalRequestRecord]:
        """Apply controlled filters to records."""
        res = records

        if query.status is not None:
            res = [r for r in res if r.status == query.status]

        if query.operation is not None:
            op_clean = query.operation.strip().lower()
            res = [r for r in res if r.operation.lower() == op_clean]

        if query.min_priority is not None:
            min_val = PRIORITY_ORDER.get(query.min_priority, 0)
            res = [r for r in res if PRIORITY_ORDER.get(r.priority, 0) >= min_val]

        if query.created_after is not None:
            res = [r for r in res if r.created_at >= query.created_after]

        if query.created_before is not None:
            res = [r for r in res if r.created_at <= query.created_before]

        return res

    def _apply_keyset_pagination(
        self, sorted_records: list[ApprovalRequestRecord], query: ReviewQueueQuery
    ) -> list[ApprovalRequestRecord]:
        """Apply keyset pagination using cursor_created_at and cursor_id."""
        if query.cursor_created_at is None or query.cursor_id is None:
            return sorted_records[: query.page_size]

        # Find items strictly AFTER cursor position in sorted order
        # Sorting key is: (-priority, created_at, id)
        start_idx = 0
        for idx, r in enumerate(sorted_records):
            if r.approval_request_id == query.cursor_id:
                start_idx = idx + 1
                break

        return sorted_records[start_idx : start_idx + query.page_size]

    def calculate_query_fingerprint(
        self,
        tenant_id: uuid.UUID,
        total_count: int,
        page_size: int,
        items: list[ReviewQueueItem],
    ) -> str:
        """Calculate SHA-256 fingerprint over query result payload."""
        payload = {
            "tenant_id": str(tenant_id),
            "total_count": total_count,
            "page_size": page_size,
            "item_ids": [str(i.approval_request_id) for i in items],
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
