"""Unified Agent Memory application service for AGENTPAY (Phase 153).

Responsibilities:
    - Unified memory architecture abstraction managing AgentMemory ORM entities
    - Production CRUD operations: create, get, update, delete, list memories
    - Version counter management and key/namespace unique constraint upsert
    - Automatic TTL expiration handling and purge_expired_memories
    - Strict tenant isolation and IDOR defense
    - Audit logging of memory creation, update, and deletion
"""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.application.services.agent_audit_service import AgentAuditService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    MemoryNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_memory import AgentMemory
from app.schemas.memory import (
    AgentMemoryCreateRequest,
    AgentMemoryRecallItem,
    AgentMemoryRecallRequest,
    AgentMemoryRecallResponse,
    AgentMemoryResponse,
    AgentMemoryUpdateRequest,
    MemoryRecallWeights,
    MemoryStatus,
)

logger = logging.getLogger("agentpay.agent.memory.service")


class AgentMemoryService:
    """Application service for managing Unified Agent Memory (Phase 153)."""

    def __init__(
        self,
        audit_service: AgentAuditService | None = None,
    ) -> None:
        self.audit_service = audit_service or AgentAuditService()

    async def create_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        request: AgentMemoryCreateRequest,
    ) -> AgentMemoryResponse:
        """Create or upsert a unified agent memory record (Phase 153).

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
        """
        # 1. Tenant Isolation & IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=request.ttl_seconds) if request.ttl_seconds else None

        # 2. Check for existing memory with same tenant_id, agent_id, namespace, key
        m_stmt = select(AgentMemory).where(
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.namespace == request.namespace,
            AgentMemory.key == request.key,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await db.execute(m_stmt)
        existing_memory = m_res.scalar_one_or_none()

        if existing_memory:
            # Update existing memory with version increment
            existing_memory.value = request.value
            existing_memory.importance = request.importance
            existing_memory.confidence = request.confidence
            existing_memory.session_id = request.session_id or existing_memory.session_id
            existing_memory.task_id = request.task_id or existing_memory.task_id
            existing_memory.expires_at = expires_at or existing_memory.expires_at
            existing_memory.version += 1
            existing_memory.updated_at = now
            if hasattr(existing_memory, "_sa_instance_state"):
                flag_modified(existing_memory, "value")
            memory_obj = existing_memory
            event_type = "memory_updated"
        else:
            # Create new memory
            memory_obj = AgentMemory(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                agent_id=agent_id,
                session_id=request.session_id,
                task_id=request.task_id,
                memory_type=request.memory_type.value,
                namespace=request.namespace,
                key=request.key,
                value=request.value,
                importance=request.importance,
                confidence=request.confidence,
                version=1,
                expires_at=expires_at,
                created_at=now,
                updated_at=now,
            )
            db.add(memory_obj)
            event_type = "memory_created"

        # 3. Audit Event
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type=event_type,
            event_action="create_or_update_memory",
            event_result="success",
            event_metadata={
                "memory_id": str(memory_obj.id),
                "key": request.key,
                "namespace": request.namespace,
                "version": memory_obj.version,
            },
        )

        await db.commit()
        await db.refresh(memory_obj)

        logger.info(
            "Agent memory record saved",
            extra={
                "memory_id": str(memory_obj.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "key": request.key,
            },
        )

        return self._to_response(memory_obj)

    async def get_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> AgentMemoryResponse:
        """Retrieve a specific memory record by ID within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            MemoryNotFoundError: if memory is missing, deleted, or expired.
        """
        await self._verify_agent_exists(db, tenant_id, agent_id)

        now = datetime.now(UTC)
        m_stmt = select(AgentMemory).where(
            AgentMemory.id == memory_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await db.execute(m_stmt)
        memory = m_res.scalar_one_or_none()

        if memory is None or (memory.expires_at and memory.expires_at < now):
            raise MemoryNotFoundError(f"Memory record {memory_id} not found.")

        return self._to_response(memory)

    async def update_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        memory_id: uuid.UUID,
        request: AgentMemoryUpdateRequest,
    ) -> AgentMemoryResponse:
        """Update an existing memory record within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            MemoryNotFoundError: if memory is missing.
        """
        await self._verify_agent_exists(db, tenant_id, agent_id)

        m_stmt = select(AgentMemory).where(
            AgentMemory.id == memory_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await db.execute(m_stmt)
        memory = m_res.scalar_one_or_none()
        if memory is None:
            raise MemoryNotFoundError(f"Memory record {memory_id} not found.")

        now = datetime.now(UTC)
        if request.value is not None:
            memory.value = request.value
            if hasattr(memory, "_sa_instance_state"):
                flag_modified(memory, "value")
        if request.importance is not None:
            memory.importance = request.importance
        if request.confidence is not None:
            memory.confidence = request.confidence
        if request.ttl_seconds is not None:
            memory.expires_at = now + timedelta(seconds=request.ttl_seconds)

        memory.version += 1
        memory.updated_at = now
        db.add(memory)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="memory_updated",
            event_action="update_memory",
            event_result="success",
            event_metadata={"memory_id": str(memory_id), "new_version": memory.version},
        )

        await db.commit()
        await db.refresh(memory)

        return self._to_response(memory)

    async def delete_memory(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> None:
        """Soft-delete a memory record within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            MemoryNotFoundError: if memory is missing.
        """
        await self._verify_agent_exists(db, tenant_id, agent_id)

        m_stmt = select(AgentMemory).where(
            AgentMemory.id == memory_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await db.execute(m_stmt)
        memory = m_res.scalar_one_or_none()
        if memory is None:
            raise MemoryNotFoundError(f"Memory record {memory_id} not found.")

        memory.deleted_at = datetime.now(UTC)
        db.add(memory)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="memory_deleted",
            event_action="delete_memory",
            event_result="success",
            event_metadata={"memory_id": str(memory_id)},
        )

        await db.commit()

    async def list_memories(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        namespace: str | None = None,
        memory_type: str | None = None,
        session_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
    ) -> list[AgentMemoryResponse]:
        """List active memories for an agent within tenant scope."""
        await self._verify_agent_exists(db, tenant_id, agent_id)

        now = datetime.now(UTC)
        query = select(AgentMemory).where(
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )

        if namespace:
            query = query.where(AgentMemory.namespace == namespace)
        if memory_type:
            query = query.where(AgentMemory.memory_type == memory_type)
        if session_id:
            query = query.where(AgentMemory.session_id == session_id)
        if task_id:
            query = query.where(AgentMemory.task_id == task_id)

        res = await db.execute(query)
        memories = res.scalars().all()

        active_memories = [m for m in memories if not (m.expires_at and m.expires_at < now)]
        return [self._to_response(m) for m in active_memories]

    async def purge_expired_memories(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> int:
        """Soft-delete all expired memory records for an agent."""
        now = datetime.now(UTC)
        query = select(AgentMemory).where(
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.expires_at.is_not(None),
            AgentMemory.expires_at < now,
            AgentMemory.deleted_at.is_(None),
        )
        res = await db.execute(query)
        expired_records = res.scalars().all()

        for m in expired_records:
            m.deleted_at = now
            db.add(m)

        if expired_records:
            await db.commit()

        return len(expired_records)

    async def archive_memory(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> AgentMemoryResponse:
        """Archive a long-term memory record (Phase 155)."""
        await self._verify_agent_exists(db, tenant_id, agent_id)

        m_stmt = select(AgentMemory).where(
            AgentMemory.id == memory_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await self._exec(db, m_stmt)
        memory = m_res.scalar_one_or_none()
        if memory is None:
            raise MemoryNotFoundError(f"Memory record {memory_id} not found.")

        val_copy = dict(memory.value or {})
        val_copy["status"] = MemoryStatus.ARCHIVED.value
        memory.value = val_copy
        memory.version += 1
        memory.updated_at = datetime.now(UTC)

        if hasattr(memory, "_sa_instance_state"):
            flag_modified(memory, "value")

        db.add(memory)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="memory_archived",
            event_action="archive_memory",
            event_result="success",
            event_metadata={"memory_id": str(memory_id)},
        )
        if hasattr(db.commit, "__await__"):
            await db.commit()
        else:
            db.commit()
        return self._to_response(memory)

    async def restore_memory(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> AgentMemoryResponse:
        """Restore an archived long-term memory record (Phase 155)."""
        await self._verify_agent_exists(db, tenant_id, agent_id)

        m_stmt = select(AgentMemory).where(
            AgentMemory.id == memory_id,
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )
        m_res = await self._exec(db, m_stmt)
        memory = m_res.scalar_one_or_none()
        if memory is None:
            raise MemoryNotFoundError(f"Memory record {memory_id} not found.")

        val_copy = dict(memory.value or {})
        val_copy["status"] = MemoryStatus.ACTIVE.value
        memory.value = val_copy
        memory.version += 1
        memory.updated_at = datetime.now(UTC)

        if hasattr(memory, "_sa_instance_state"):
            flag_modified(memory, "value")

        db.add(memory)

        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="memory_restored",
            event_action="restore_memory",
            event_result="success",
            event_metadata={"memory_id": str(memory_id)},
        )
        if hasattr(db.commit, "__await__"):
            await db.commit()
        else:
            db.commit()
        return self._to_response(memory)

    async def recall_memories(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: AgentMemoryRecallRequest,
    ) -> AgentMemoryRecallResponse:
        """Perform multi-factor weighted memory recall and relevance ranking (Phase 155)."""
        await self._verify_agent_exists(db, tenant_id, agent_id)

        now = datetime.now(UTC)
        query = select(AgentMemory).where(
            AgentMemory.agent_id == agent_id,
            AgentMemory.tenant_id == tenant_id,
            AgentMemory.deleted_at.is_(None),
        )

        if request.namespace:
            query = query.where(AgentMemory.namespace == request.namespace)

        res = await self._exec(db, query)
        raw_memories = res.scalars().all()

        w = request.weights or MemoryRecallWeights()
        recalled_items: list[AgentMemoryRecallItem] = []

        for m in raw_memories:
            # Check expiration & status
            if m.expires_at and m.expires_at < now:
                continue
            val = m.value or {}
            if val.get("status") in (MemoryStatus.ARCHIVED.value, MemoryStatus.DELETED.value):
                continue

            if request.memory_types and m.memory_type not in request.memory_types:
                continue

            # Multi-factor score computation
            importance_score = float(m.importance) if m.importance is not None else 0.5
            confidence_score = float(m.confidence) if m.confidence is not None else 1.0

            # Recency score (decay based on age in days)
            age_hours = (
                (now - m.created_at.replace(tzinfo=UTC)).total_seconds() / 3600.0
                if m.created_at
                else 0.0
            )  # noqa: E501
            recency_score = max(0.0, 1.0 - (age_hours / 720.0))  # 30-day linear decay

            # Text relevance match score
            match_score = 0.5
            if request.query:
                q_lower = request.query.lower()
                text_corpus = f"{m.key} {m.namespace} {str(m.value)}".lower()
                if q_lower in text_corpus:
                    match_score = 1.0
                elif any(term in text_corpus for term in q_lower.split()):
                    match_score = 0.7
                else:
                    match_score = 0.2

            # Weighted combination
            final_relevance = (
                (importance_score * w.importance_weight)
                + (confidence_score * w.confidence_weight)
                + (recency_score * w.recency_weight)
                + (match_score * w.decay_weight)
            )
            final_relevance = round(min(1.0, max(0.0, final_relevance)), 4)

            if final_relevance >= request.min_relevance:
                recalled_items.append(
                    AgentMemoryRecallItem(
                        memory=self._to_response(m),
                        relevance_score=final_relevance,
                    )
                )

        # Sort descending by relevance score and take top_k
        recalled_items.sort(key=lambda x: x.relevance_score, reverse=True)
        top_results = recalled_items[: request.top_k]

        return AgentMemoryRecallResponse(
            query=request.query,
            total_recalled=len(top_results),
            results=top_results,
        )

    async def _exec(self, db: Any, stmt: Any) -> Any:
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        return res

    async def _verify_agent_exists(
        self, db: Any, tenant_id: uuid.UUID, agent_id: uuid.UUID
    ) -> None:
        """Verify agent existence and tenant ownership fail-closed."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        res = await self._exec(db, agent_stmt)
        if res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

    def _to_response(self, memory: AgentMemory) -> AgentMemoryResponse:
        """Map ORM entity to AgentMemoryResponse."""
        return AgentMemoryResponse(
            id=memory.id,
            tenant_id=memory.tenant_id,
            agent_id=memory.agent_id,
            session_id=memory.session_id,
            task_id=memory.task_id,
            memory_type=memory.memory_type,
            namespace=memory.namespace,
            key=memory.key,
            value=memory.value,
            importance=memory.importance,
            confidence=memory.confidence,
            version=memory.version,
            expires_at=memory.expires_at,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        )
