"""Integration tests for ATIM Group 13 / Phase 24 Multi-Agent Consensus REST API Endpoints."""

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.main import app


@pytest.mark.asyncio
async def test_consensus_api_lifecycle_e2e(db_session):
    """Test full HTTP REST API lifecycle for creating sessions, voting, and querying details."""
    tenant_id = uuid.uuid4()
    proposer_agent_id = uuid.uuid4()
    voter1_id = uuid.uuid4()
    voter2_id = uuid.uuid4()

    dummy_user = User(id=uuid.uuid4(), email="consensus_admin@agentpay.com", tenant_id=tenant_id)
    dummy_session = SessionModel(id=uuid.uuid4(), user_id=dummy_user.id)
    mock_auth = AuthenticatedUser(user=dummy_user, session=dummy_session, tenant_id=tenant_id)

    app.dependency_overrides[get_current_user] = lambda: mock_auth

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Create Session
        create_payload = {
            "tenant_id": str(tenant_id),
            "proposer_agent_id": str(proposer_agent_id),
            "action": "GOVERNANCE_TRANSFER",
            "required_quorum": 2,
        }
        resp = await client.post("/api/v1/atim/consensus/sessions", json=create_payload)
        assert resp.status_code == 201
        data = resp.json()
        session_id = data["session_id"]
        assert data["status"] == "VOTING"

        # 2. Vote 1 (Approve)
        vote1_payload = {
            "voter_agent_id": str(voter1_id),
            "vote": "APPROVE",
            "reason": "Verified compliance token",
        }
        resp = await client.post(f"/api/v1/atim/consensus/sessions/{session_id}/vote", json=vote1_payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "VOTING"

        # 3. Vote 2 (Approve -> Quorum Reached)
        vote2_payload = {
            "voter_agent_id": str(voter2_id),
            "vote": "APPROVE",
            "reason": "Treasury balance verified",
        }
        resp = await client.post(f"/api/v1/atim/consensus/sessions/{session_id}/vote", json=vote2_payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "QUORUM_REACHED"

        # 4. Query Session Details
        resp = await client.get(f"/api/v1/atim/consensus/sessions/{session_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "QUORUM_REACHED"

    app.dependency_overrides.clear()
