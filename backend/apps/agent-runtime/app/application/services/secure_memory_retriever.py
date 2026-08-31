"""Secure Memory Retriever with tenant isolation, trust classification, memory poisoning defense, and context budgeting."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_memory_service import AgentMemoryService
from app.application.services.atim_security.injection_detector import ATIMInjectionDetector
from app.application.services.atim_security.secret_detector import ATIMSecretDetector
from app.application.services.atim_security.trust_boundary import ContextTrustLevel
from app.schemas.memory import AgentMemoryRecallRequest, MemoryStatus

logger = logging.getLogger("agentpay.atim.memory.secure_retriever")


class MemoryType(StrEnum):
    """Memory type classification categories (Phase 5)."""

    USER_PREFERENCE = "USER_PREFERENCE"
    TRANSACTION_CONTEXT = "TRANSACTION_CONTEXT"
    MERCHANT_PREFERENCE = "MERCHANT_PREFERENCE"
    PRODUCT_PREFERENCE = "PRODUCT_PREFERENCE"
    AGENT_BEHAVIOR = "AGENT_BEHAVIOR"
    WORKFLOW_CONTEXT = "WORKFLOW_CONTEXT"
    CONVERSATION_SUMMARY = "CONVERSATION_SUMMARY"
    SECURITY_EVENT = "SECURITY_EVENT"
    SYSTEM_FACT = "SYSTEM_FACT"
    TEMPORARY_CONTEXT = "TEMPORARY_CONTEXT"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class MemoryTrustLevel(StrEnum):
    """Memory provenance and trust classification levels."""

    VERIFIED = "VERIFIED"
    USER_PROVIDED = "USER_PROVIDED"
    LLM_GENERATED = "LLM_GENERATED"
    TOOL_DERIVED = "TOOL_DERIVED"
    EXTERNAL = "EXTERNAL"
    QUARANTINED = "QUARANTINED"


class SecureMemoryItem(BaseModel):
    """Secure memory item prepared for context inclusion."""

    memory_id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    namespace: str
    key: str
    value: dict[str, Any]
    memory_type: str
    trust_level: MemoryTrustLevel = MemoryTrustLevel.USER_PROVIDED
    importance: float = 0.5
    confidence: float = 1.0
    relevance_score: float = 0.0
    quarantined: bool = False
    quarantine_reason: str | None = None
    created_at: datetime


class SecureMemoryRecallResult(BaseModel):
    """Result payload produced by SecureMemoryRetriever."""

    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    total_retrieved: int = 0
    quarantined_count: int = 0
    budget_truncated: bool = False
    memories: list[SecureMemoryItem] = Field(default_factory=list)
    compressed_summary: str = Field(default="")


class SecureMemoryRetriever:
    """Production secure memory retriever featuring SQL tenant isolation, memory poisoning quarantine, and context budgeting."""

    def __init__(
        self,
        memory_service: AgentMemoryService | None = None,
        injection_detector: ATIMInjectionDetector | None = None,
        secret_detector: ATIMSecretDetector | None = None,
        max_memory_items: int = 10,
        max_memory_tokens: int = 3000,
    ) -> None:
        self.memory_service = memory_service or AgentMemoryService()
        self.injection_detector = injection_detector or ATIMInjectionDetector()
        self.secret_detector = secret_detector or ATIMSecretDetector()
        self.max_memory_items = max_memory_items
        self.max_memory_tokens = max_memory_tokens

    async def retrieve_secure_memories(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        query: str,
        namespaces: list[str] | None = None,
        top_k: int = 5,
        min_relevance: float = 0.3,
    ) -> SecureMemoryRecallResult:
        """Fetch, security-scan, score, resolve conflicts, and budget memory context fail-closed.

        Mandatory Invariant: SQL filtering on tenant_id and agent_id MUST occur at the database query layer.
        """
        # 1. Mandatory SQL-level Tenant & Agent Isolation Query
        recall_req = AgentMemoryRecallRequest(
            query=query,
            top_k=50,  # Fetch pool for scoring and security scanning
            min_relevance=0.1,
        )

        try:
            recall_resp = await self.memory_service.recall_memories(
                db, tenant_id=tenant_id, agent_id=agent_id, request=recall_req
            )
        except Exception as exc:
            logger.error("Failed secure memory query for tenant %s agent %s: %s", tenant_id, agent_id, exc)
            return SecureMemoryRecallResult(
                tenant_id=tenant_id,
                agent_id=agent_id,
                total_retrieved=0,
                quarantined_count=0,
            )

        now = datetime.now(UTC)
        candidate_items: list[SecureMemoryItem] = []
        quarantined_count = 0

        # Trust Multiplier map
        TRUST_MULTIPLIERS = {
            MemoryTrustLevel.VERIFIED: 1.2,
            MemoryTrustLevel.USER_PROVIDED: 1.0,
            MemoryTrustLevel.LLM_GENERATED: 0.8,
            MemoryTrustLevel.TOOL_DERIVED: 0.7,
            MemoryTrustLevel.EXTERNAL: 0.6,
            MemoryTrustLevel.QUARANTINED: 0.0,
        }

        # 2. Security Scan & Poisoning Quarantine
        for recall_item in recall_resp.results:
            mem = recall_item.memory
            val_dict = mem.value if isinstance(mem.value, dict) else {"content": str(mem.value)}
            val_str = f"{mem.key} {mem.namespace} {str(val_dict)}"

            # A. Secret Scan in Memory
            sec_res = self.secret_detector.scan_and_redact(val_str)
            # B. Injection Scan in Memory
            inj_res = self.injection_detector.detect_injection(sec_res.sanitized_text)

            is_quarantined = False
            quarantine_reason = None
            trust_level = MemoryTrustLevel.USER_PROVIDED

            # Infer trust level from value metadata if available
            if isinstance(val_dict, dict) and "trust_level" in val_dict:
                try:
                    trust_level = MemoryTrustLevel(val_dict["trust_level"])
                except Exception:
                    pass

            if inj_res.detected or sec_res.secrets_detected:
                is_quarantined = True
                trust_level = MemoryTrustLevel.QUARANTINED
                quarantine_reason = (
                    f"INJECTION_DETECTED: {inj_res.categories}"
                    if inj_res.detected
                    else f"SECRETS_DETECTED: {sec_res.secret_types}"
                )
                quarantined_count += 1
                logger.warning(
                    "Quarantined malicious memory %s for tenant %s agent %s (%s)",
                    mem.id,
                    tenant_id,
                    agent_id,
                    quarantine_reason,
                )

            # C. Multi-Factor Scoring
            if is_quarantined:
                final_score = 0.0
            else:
                base_rel = recall_item.relevance_score
                trust_mult = TRUST_MULTIPLIERS.get(trust_level, 1.0)
                conf_mult = float(mem.confidence) if mem.confidence is not None else 1.0
                imp_mult = float(mem.importance) if mem.importance is not None else 0.5

                # Recency multiplier
                age_hours = (now - mem.created_at.replace(tzinfo=UTC)).total_seconds() / 3600.0 if mem.created_at else 0.0
                recency_mult = max(0.5, 1.0 - (age_hours / 720.0))

                final_score = round(base_rel * trust_mult * conf_mult * imp_mult * recency_mult, 4)

            if not is_quarantined and final_score >= min_relevance:
                candidate_items.append(
                    SecureMemoryItem(
                        memory_id=mem.id,
                        tenant_id=mem.tenant_id,
                        agent_id=mem.agent_id,
                        namespace=mem.namespace,
                        key=mem.key,
                        value=val_dict,
                        memory_type=mem.memory_type,
                        trust_level=trust_level,
                        importance=float(mem.importance or 0.5),
                        confidence=float(mem.confidence or 1.0),
                        relevance_score=final_score,
                        quarantined=False,
                        created_at=mem.created_at,
                    )
                )

        # 3. Deterministic Conflict Resolution (group by namespace:key, select highest trust/recency/score)
        resolved_map: dict[str, SecureMemoryItem] = {}
        for item in candidate_items:
            composite_key = f"{item.namespace}:{item.key}"
            if composite_key not in resolved_map:
                resolved_map[composite_key] = item
            else:
                existing = resolved_map[composite_key]
                # Compare trust level, then recency, then relevance score
                if item.trust_level == MemoryTrustLevel.VERIFIED and existing.trust_level != MemoryTrustLevel.VERIFIED:
                    resolved_map[composite_key] = item
                elif item.relevance_score > existing.relevance_score:
                    resolved_map[composite_key] = item

        sorted_items = sorted(resolved_map.values(), key=lambda x: x.relevance_score, reverse=True)

        # 4. Context Token & Item Budget Enforcement
        effective_top_k = min(top_k, self.max_memory_items)
        budgeted_items: list[SecureMemoryItem] = []
        accumulated_tokens = 0
        budget_truncated = False

        for item in sorted_items:
            if len(budgeted_items) >= effective_top_k:
                budget_truncated = True
                break

            # Estimate token count (~4 chars per token)
            item_str = f"{item.namespace}:{item.key}:{str(item.value)}"
            item_tokens = max(1, len(item_str) // 4)

            if accumulated_tokens + item_tokens > self.max_memory_tokens:
                budget_truncated = True
                break

            budgeted_items.append(item)
            accumulated_tokens += item_tokens

        # 5. Deterministic Context Summarization
        summary_lines = []
        for b_item in budgeted_items:
            summary_lines.append(f"- [{b_item.namespace}:{b_item.key}] {str(b_item.value)}")
        compressed_summary = "\n".join(summary_lines)

        return SecureMemoryRecallResult(
            tenant_id=tenant_id,
            agent_id=agent_id,
            total_retrieved=len(budgeted_items),
            quarantined_count=quarantined_count,
            budget_truncated=budget_truncated,
            memories=budgeted_items,
            compressed_summary=compressed_summary,
        )
