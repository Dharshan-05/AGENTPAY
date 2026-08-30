"""Unit and Security Tests for Policy Evaluation Engine (Phase 187)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.policy_evaluation_service import PolicyEvaluationService
from app.infrastructure.database.models.security_policy import SecurityPolicy
from app.schemas.agent_identity_verification import AgentIdentityVerificationResult
from app.schemas.policy_evaluation import PolicyEvaluationContext


@pytest.fixture
def service() -> PolicyEvaluationService:
    service = PolicyEvaluationService()
    service.identity_service.verify_agent_identity = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_evaluate_no_active_policies_returns_no_applicable_policy(
    service: PolicyEvaluationService,
) -> None:
    """1. Test evaluation with no active policies returns NO_APPLICABLE_POLICY."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=None,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=now,
        )
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    context = PolicyEvaluationContext(
        tenant_id=tenant_id, agent_id=agent_id, amount=Decimal("100.00")
    )
    res = await service.evaluate_policies(mock_db, tenant_id, agent_id, context)
    assert res.decision == "NO_APPLICABLE_POLICY"


@pytest.mark.asyncio
async def test_02_evaluate_active_policy_allows(
    service: PolicyEvaluationService,
) -> None:
    """2. Test active policy with enforce mode allows transaction under threshold."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=None,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=now,
        )
    )

    policy = SecurityPolicy(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Spending Limit",
        slug="spending-limit",
        status="active",
        policy_type="spending",
        priority=100,
        enforcement_mode="enforce",
        configuration={"max_transaction_amount": "500.00"},
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [policy]

    context = PolicyEvaluationContext(
        tenant_id=tenant_id, agent_id=agent_id, amount=Decimal("100.00")
    )
    res = await service.evaluate_policies(mock_db, tenant_id, agent_id, context)
    assert res.decision == "ALLOW"


@pytest.mark.asyncio
async def test_03_evaluate_block_policy_denies(
    service: PolicyEvaluationService,
) -> None:
    """3. Test policy with block mode denies transaction exceeding threshold."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    now = datetime.now(UTC)

    service.identity_service.verify_agent_identity.return_value = (  # type: ignore[attr-defined]
        AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=None,
            verified=True,
            agent_status="active",
            verification_reason="OK",
            verified_at=now,
        )
    )

    policy = SecurityPolicy(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Block Big Purchases",
        slug="block-big-purchases",
        status="active",
        policy_type="spending",
        priority=200,
        enforcement_mode="block",
        configuration={"max_transaction_amount": "500.00"},
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = [policy]

    context = PolicyEvaluationContext(
        tenant_id=tenant_id, agent_id=agent_id, amount=Decimal("600.00")
    )
    res = await service.evaluate_policies(mock_db, tenant_id, agent_id, context)
    assert res.decision == "DENIED"
    assert "SPENDING_LIMIT_EXCEEDED" in res.reason_codes
