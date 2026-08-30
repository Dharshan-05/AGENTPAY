"""Unit & Integration tests for Phase 135 — Agent Management Integration."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_credential_service import AgentCredentialService
from app.application.services.agent_lifecycle_service import AgentLifecycleService
from app.application.services.agent_metadata_service import AgentMetadataService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.application.services.agent_service import AgentService
from app.application.services.agent_session_service import AgentSessionService
from app.application.services.agent_trust_service import AgentTrustService
from app.schemas.agents import (
    AgentCreateRequest,
    AgentCredentialCreateRequest,
    AgentSessionCreateRequest,
)


@pytest.mark.asyncio
async def test_full_agent_management_lifecycle_integration(
    db_session: AsyncSession,
) -> None:
    """Test end-to-end integration of Phase 119-134 subsystem flows.

    Flow:
        CREATE -> CREDENTIAL -> ACTIVATE -> SESSION -> METADATA -> TRUST -> SUSPEND -> REVOKE
    """
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    agent_service = AgentService()
    cred_service = AgentCredentialService()
    lifecycle_service = AgentLifecycleService()
    session_service = AgentSessionService()
    metadata_service = AgentMetadataService()
    trust_service = AgentTrustService()
    audit_service = AgentAuditService()
    security_service = AgentSecurityEventService()

    # 1. Create Agent
    create_req = AgentCreateRequest(
        name="Integrated Test Agent",
        slug="integrated-test-agent",
        agent_type="autonomous",
    )
    agent = await agent_service.create_agent(db_session, tenant_id, create_req)
    assert agent.status == "provisioning"

    # 2. Issue Credential
    cred_req = AgentCredentialCreateRequest(credential_type="api_key")
    cred, raw_secret = await cred_service.create_credential(
        db_session, tenant_id, agent.id, cred_req
    )
    assert cred.status == "active"
    assert raw_secret is not None

    # 3. Activate Agent
    agent, lifecycle = await lifecycle_service.activate_agent(
        db_session, tenant_id, agent.id, reason="Initial activation", actor_id=actor_id
    )
    assert agent.status == "active"
    assert lifecycle.status == "active"

    # 4. Issue Runtime Session
    sess_req = AgentSessionCreateRequest(credential_id=cred.id)
    session = await session_service.create_session(db_session, tenant_id, agent.id, sess_req)
    assert session.status == "active"

    # 5. Update Metadata
    meta = await metadata_service.update_agent_metadata(
        db_session, tenant_id, agent.id, {"integration": "verified", "tier": "gold"}
    )
    assert meta.metadata_payload.get("integration") == "verified"

    # 6. Update Trust Posture
    trust = await trust_service.update_agent_trust(
        db_session,
        tenant_id,
        agent.id,
        trust_status="high",
        trust_score=Decimal("98.00"),
        trust_reason="Automated verification pass",
    )
    assert trust.trust_status == "high"

    # 7. Suspend Agent (should revoke active sessions)
    agent, lifecycle, rev_sess = await lifecycle_service.suspend_agent(
        db_session, tenant_id, agent.id, reason="Emergency audit", actor_id=actor_id
    )
    assert agent.status == "suspended"
    assert rev_sess == 1

    # 8. Revoke Agent permanently (should deactivate credentials and sessions)
    agent, lifecycle, _, rev_creds = await lifecycle_service.revoke_agent(
        db_session, tenant_id, agent.id, reason="Decommissioned", actor_id=actor_id
    )
    assert agent.status == "deactivated"
    assert rev_creds == 1

    # 9. Verify Audit Events recorded during lifecycle
    audit_logs, _ = await audit_service.list_agent_audit_events(db_session, tenant_id, agent.id)
    assert len(audit_logs) >= 3

    # 10. Verify Security Events recorded during lifecycle
    sec_events, _ = await security_service.list_agent_security_events(
        db_session, tenant_id, agent.id
    )
    assert len(sec_events) >= 3
