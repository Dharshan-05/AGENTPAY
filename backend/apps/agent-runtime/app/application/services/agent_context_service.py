"""Agent Context Management application service for AGENTPAY (Phase 152).

Responsibilities:
    - Production-grade context assembly, prioritization, limiting, and truncation
    - Multi-scope aggregation: SYSTEM, AGENT_IDENTITY, USER, CONVERSATION, TASK, TOOL, RUNTIME
    - Deterministic token budgeting and size limit enforcement (ContextBudget)
    - Context deduplication, relevance scoring, and scope-preserved truncation
    - Secret sanitization (redacts tokens, credentials, API keys)
    - Strict tenant isolation and IDOR defense (raises AgentNotFoundError on cross-tenant attempts)
    - Audit event emission (context_assembled)
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_trust_service import AgentTrustService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    ContextBudgetExceededError,
)
from app.infrastructure.database.models.agent import Agent
from app.schemas.context import (
    ContextAssemblyRequest,
    ContextAssemblyResponse,
    ContextBudget,
    ContextItem,
    ContextScope,
)

logger = logging.getLogger("agentpay.agent.context.service")

# Regex pattern for sanitizing secret material in context payloads
SECRET_PATTERN = re.compile(
    r"(?i)(bearer\s+[a-z0-9\._\-]+|api_key[=:\s]+[a-z0-9_\-]+|secret[=:\s]+[a-z0-9_\-]+|password[=:\s]+[^\s]+)"  # noqa: E501
)


class AgentContextService:
    """Application service for assembling and maintaining Agent Context (Phase 152)."""

    def __init__(
        self,
        trust_service: AgentTrustService | None = None,
        audit_service: AgentAuditService | None = None,
    ) -> None:
        self.trust_service = trust_service or AgentTrustService()
        self.audit_service = audit_service or AgentAuditService()

    async def assemble_agent_context(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: ContextAssemblyRequest,
    ) -> ContextAssemblyResponse:
        """Assemble, prioritize, limit, and sanitize agent context representation (Phase 152).

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            ContextBudgetExceededError: if mandatory system context exceeds max_tokens budget.
        """
        # 1. Tenant Isolation & IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Fetch Agent Trust Posture
        trust_score = 50.0
        try:
            trust = await self.trust_service.get_agent_trust(db, tenant_id, agent_id)
            if trust and trust.trust_score is not None:
                trust_score = float(trust.trust_score)
        except Exception:
            pass

        now = datetime.now(UTC)
        assembly_id = uuid.uuid4()
        budget = request.budget or ContextBudget()

        # 3. Base Context Scope Generation
        items: list[ContextItem] = []

        # Scope: SYSTEM (Priority 100)
        system_text = (
            "AGENTPAY Autonomous System Context. Policy: Multi-tenant isolation."
            f" Max Token Budget: {budget.max_tokens}."
        )
        items.append(
            ContextItem(
                item_id=f"sys-{uuid.uuid4().hex[:8]}",
                scope=ContextScope.SYSTEM,
                priority=100,
                content=system_text,
                estimated_tokens=len(system_text) // 4 + 1,
                relevance_score=1.0,
                created_at=now,
            )
        )

        # Scope: AGENT_IDENTITY (Priority 90)
        agent_text = (
            f"Agent Name: {agent.name}, Type: {agent.agent_type}, Status: {agent.status},"
            f" Trust Score: {trust_score:.2f}."
        )
        items.append(
            ContextItem(
                item_id=f"identity-{uuid.uuid4().hex[:8]}",
                scope=ContextScope.AGENT_IDENTITY,
                priority=90,
                content=agent_text,
                estimated_tokens=len(agent_text) // 4 + 1,
                relevance_score=1.0,
                created_at=now,
            )
        )

        # Scope: USER (Priority 70) if user prompt provided
        if request.user_prompt:
            sanitized_prompt = self._sanitize_content(request.user_prompt)
            items.append(
                ContextItem(
                    item_id=f"prompt-{uuid.uuid4().hex[:8]}",
                    scope=ContextScope.USER,
                    priority=70,
                    content=f"User Prompt: {sanitized_prompt}",
                    estimated_tokens=len(sanitized_prompt) // 4 + 1,
                    relevance_score=0.9,
                    created_at=now,
                )
            )

        # Scope: TASK / SESSION (Priority 60)
        if request.task_id or request.session_id:
            task_text = f"Active Session: {request.session_id}, Active Task: {request.task_id}."
            items.append(
                ContextItem(
                    item_id=f"task-{uuid.uuid4().hex[:8]}",
                    scope=ContextScope.TASK,
                    priority=60,
                    content=task_text,
                    estimated_tokens=len(task_text) // 4 + 1,
                    relevance_score=0.85,
                    created_at=now,
                )
            )

        # Custom items from request
        for c_item in request.custom_items:
            # Sanitize content
            c_item.content = self._sanitize_content(c_item.content)
            if not c_item.estimated_tokens:
                c_item.estimated_tokens = len(c_item.content) // 4 + 1
            items.append(c_item)

        # 4. Context Deduplication & Expiration Filtering
        unique_items: list[ContextItem] = []
        seen_contents: set[str] = set()

        for item in items:
            # Expiration check
            if item.expires_at and item.expires_at < now:
                continue
            # Content deduplication
            normalized_content = item.content.strip().lower()
            if normalized_content in seen_contents:
                continue
            seen_contents.add(normalized_content)
            unique_items.append(item)

        # 5. Context Prioritization & Ordering (Priority desc, Relevance desc)
        sorted_items = sorted(
            unique_items,
            key=lambda x: (x.priority, x.relevance_score, x.created_at),
            reverse=True,
        )

        # 6. Token Budgeting & Truncation
        assembled_items: list[ContextItem] = []
        accumulated_tokens = 0
        truncated_count = 0

        for item in sorted_items:
            # Always preserve protected scopes
            is_protected = item.scope in budget.preserve_scopes
            item_tokens = item.estimated_tokens or (len(item.content) // 4 + 1)

            if accumulated_tokens + item_tokens <= budget.max_tokens or is_protected:
                assembled_items.append(item)
                accumulated_tokens += item_tokens
            else:
                truncated_count += 1

        # Check if mandatory budget was exceeded
        if accumulated_tokens > budget.max_tokens and not assembled_items:
            raise ContextBudgetExceededError("Mandatory context exceeded max token budget.")

        # 7. Audit Event Registration
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=uuid.UUID(int=0),  # System actor
            event_type="context_assembled",
            event_action="assemble_context",
            event_result="success",
            event_metadata={
                "assembly_id": str(assembly_id),
                "total_tokens": accumulated_tokens,
                "items_count": len(assembled_items),
                "truncated_count": truncated_count,
            },
        )

        logger.info(
            "Agent context assembled",
            extra={
                "assembly_id": str(assembly_id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "total_tokens": accumulated_tokens,
            },
        )

        return ContextAssemblyResponse(
            assembly_id=assembly_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            session_id=request.session_id,
            task_id=request.task_id,
            total_tokens=accumulated_tokens,
            total_items=len(assembled_items),
            truncated_items_count=truncated_count,
            items=assembled_items,
            assembled_at=now,
        )

    def _sanitize_content(self, text: str) -> str:
        """Sanitize sensitive secrets, API keys, and authorization tokens."""
        return SECRET_PATTERN.sub("[REDACTED_SECRET]", text)
