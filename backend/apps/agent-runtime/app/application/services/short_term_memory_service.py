"""Short-Term Working Memory application service for AGENTPAY (Phase 154).

Responsibilities:
    - Session-scoped and task-scoped working memory management
    - Stores intermediate agent decisions, active workflow state, and temporary variables
    - Built on top of unified AgentMemoryService (namespace: "short_term_working_memory")
    - Enforces working memory limits per session (max 50 variables to prevent exhaustion)
    - Automatic TTL expiration and cleanup support
    - Strict tenant isolation and IDOR defense
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_memory_service import AgentMemoryService
from app.domain.exceptions.agent_exceptions import (
    MemoryNotFoundError,
    MemoryQuotaExceededError,
)
from app.schemas.memory import (
    AgentMemoryCreateRequest,
    AgentMemoryResponse,
    MemoryType,
    ShortTermMemoryListResponse,
    ShortTermMemorySetRequest,
)

logger = logging.getLogger("agentpay.agent.short_term_memory.service")

MAX_SESSION_WORKING_MEMORY_VARIABLES = 50
SHORT_TERM_NAMESPACE = "short_term_working_memory"


class ShortTermMemoryService:
    """Application service for managing Session/Task Short-Term Memory (Phase 154)."""

    def __init__(
        self,
        memory_service: AgentMemoryService | None = None,
    ) -> None:
        self.memory_service = memory_service or AgentMemoryService()

    async def set_variable(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        session_id: uuid.UUID | None,
        request: ShortTermMemorySetRequest,
    ) -> AgentMemoryResponse:
        """Store or update a short-term working memory variable (Phase 154).

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            MemoryQuotaExceededError: if session variable limit is exceeded.
        """
        task_id = request.task_id

        # 1. Enforce Quota Limit
        current_memories = await self.memory_service.list_memories(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            namespace=SHORT_TERM_NAMESPACE,
            session_id=session_id,
            task_id=task_id,
        )

        existing_keys = {m.key for m in current_memories}
        if (
            request.key not in existing_keys
            and len(current_memories) >= MAX_SESSION_WORKING_MEMORY_VARIABLES
        ):
            raise MemoryQuotaExceededError(
                f"Quota exceeded (max {MAX_SESSION_WORKING_MEMORY_VARIABLES} variables)."
            )

        # 2. Save via AgentMemoryService
        create_req = AgentMemoryCreateRequest(
            key=request.key,
            value=request.value,
            namespace=SHORT_TERM_NAMESPACE,
            memory_type=MemoryType.SHORT_TERM,
            session_id=session_id,
            task_id=task_id,
            importance=0.8,
            confidence=1.0,
            ttl_seconds=request.ttl_seconds or 3600,
        )

        mem_res = await self.memory_service.create_memory(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            request=create_req,
        )

        logger.info(
            "Short-term working memory variable set",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "session_id": str(session_id) if session_id else None,
                "key": request.key,
            },
        )

        return mem_res

    async def get_variable(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        key: str,
        session_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ) -> AgentMemoryResponse:
        """Fetch a specific short-term working memory variable.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            MemoryNotFoundError: if variable is missing or expired.
        """
        memories = await self.memory_service.list_memories(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            namespace=SHORT_TERM_NAMESPACE,
            session_id=session_id,
            task_id=task_id,
        )

        for m in memories:
            if m.key == key:
                return m

        raise MemoryNotFoundError(f"Working memory variable '{key}' not found.")

    async def get_working_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ) -> ShortTermMemoryListResponse:
        """Fetch all active working memory variables for a session/task."""
        memories = await self.memory_service.list_memories(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            namespace=SHORT_TERM_NAMESPACE,
            session_id=session_id,
            task_id=task_id,
        )

        return ShortTermMemoryListResponse(
            tenant_id=tenant_id,
            agent_id=agent_id,
            session_id=session_id,
            task_id=task_id,
            total_keys=len(memories),
            memories=memories,
        )

    async def clear_working_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ) -> int:
        """Clear all working memory variables for a session or task."""
        memories = await self.memory_service.list_memories(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            namespace=SHORT_TERM_NAMESPACE,
            session_id=session_id,
            task_id=task_id,
        )

        cleared_count = 0
        for m in memories:
            await self.memory_service.delete_memory(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                user_id=user_id,
                memory_id=m.id,
            )
            cleared_count += 1

        return cleared_count
