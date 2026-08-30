"""Unit, REST API & Security Tests for Phase 284.

Risk Decision API & Adversarial Security Matrix.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import get_authorization_service
from app.api.v1.risk_decisions import risk_decisions_router
from app.domain.authorization.permissions_registry import (
    RISK_DECISIONS_EVALUATE,
    RISK_DECISIONS_READ,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.risk_engine import (
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)

# Test Fixtures & Mock App Setup
app = FastAPI()
app.include_router(risk_decisions_router, prefix="/api/v1")

TEST_TENANT_ID = uuid.uuid4()
TEST_USER_ID = uuid.uuid4()
TEST_AGENT_ID = uuid.uuid4()
TEST_TX_ID = "tx_api_284_01"


def override_get_current_user() -> AuthenticatedUser:
    mock_user = MagicMock()
    mock_user.id = TEST_USER_ID
    mock_session = MagicMock()
    return AuthenticatedUser(
        user=mock_user,
        session=mock_session,
        tenant_id=TEST_TENANT_ID,
    )


def override_get_db_session() -> MagicMock:
    return MagicMock()


class MockAuthorizationService:
    async def require_permission(self, db: MagicMock, context: Any, permission: str) -> None:
        if permission in {RISK_DECISIONS_EVALUATE, RISK_DECISIONS_READ}:
            return None
        raise PermissionError(f"Permission denied for {permission}")


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db_session] = override_get_db_session
app.dependency_overrides[get_authorization_service] = MockAuthorizationService

client = TestClient(app)


def _make_signal(
    sig_type: RiskSignalType = RiskSignalType.FRAUDGUARD,
    score: float = 10.0,
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = TEST_TX_ID,
) -> RiskSignal:
    return RiskSignal(
        signal_id=uuid.uuid4(),
        signal_type=sig_type,
        source="fraudguard",
        score=score,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=score,
        confidence=0.95,
        decision="ALLOW",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
        tenant_id=t_id or TEST_TENANT_ID,
        agent_id=a_id or TEST_AGENT_ID,
        transaction_id=tx_id,
        source_version="1.0.0",
        source_fingerprint="s1" * 32,
        availability=True,
        cold_start=False,
        metadata={},
    )


def test_01_valid_authenticated_evaluate_request() -> None:
    """1. Test valid authenticated API request evaluates risk decision successfully."""
    sig = _make_signal(score=10.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "prediction_timestamp": "2026-01-01T12:00:00Z",
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {"channel": "web"},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["tenant_id"] == str(TEST_TENANT_ID)
    assert data["agent_id"] == str(TEST_AGENT_ID)
    assert data["transaction_id"] == TEST_TX_ID
    assert data["decision"] == "ALLOW"
    assert data["reason_code"] == "LOW_RISK_ALLOW_CLEAN"
    assert data["risk_score"] == 10.0
    assert data["explanation"] is not None
    assert data["audit_event"] is not None
    assert len(data["decision_fingerprint"]) == 64


def test_02_get_audit_event_by_id_api() -> None:
    """2. Test retrieving created audit event via GET API endpoint."""
    sig = _make_signal(score=10.0)
    eval_req = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "prediction_timestamp": "2026-01-01T12:00:00Z",
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    eval_res = client.post("/api/v1/risk-decisions/evaluate", json=eval_req)
    assert eval_res.status_code == status.HTTP_200_OK
    decision_id = eval_res.json()["decision_id"]

    audit_res = client.get(f"/api/v1/risk-decisions/audit/{decision_id}")
    assert audit_res.status_code == status.HTTP_200_OK
    audit_data = audit_res.json()

    assert audit_data["decision_id"] == decision_id
    assert audit_data["tenant_id"] == str(TEST_TENANT_ID)
    assert audit_data["decision"] == "ALLOW"


def test_03_adversarial_forged_decision_attempt_rejected() -> None:
    """3. Mandatory Security Test: Forged decision field in request payload is rejected."""
    sig = _make_signal(score=99.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {
            "final_decision": "ALLOW",  # Forged decision injection attempt!
        },
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_04_adversarial_target_leakage_payload_rejected() -> None:
    """4. Mandatory Security Test: Target leakage payload is rejected."""
    sig = _make_signal(score=10.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {
            "is_fraud": True,  # Prohibited target leakage field!
        },
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_05_adversarial_cross_tenant_signal_mismatch_fails_closed() -> None:
    """5. Mandatory Security Test: Cross-tenant signal in request causes 400 Bad Request."""
    other_tenant_sig = _make_signal(score=10.0, t_id=uuid.uuid4())
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [other_tenant_sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Tenant ID mismatch" in response.json()["detail"]


def test_06_adversarial_cross_agent_signal_mismatch_fails_closed() -> None:
    """6. Mandatory Security Test: Cross-agent signal in request causes 400 Bad Request."""
    other_agent_sig = _make_signal(score=10.0, a_id=uuid.uuid4())
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [other_agent_sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Agent ID mismatch" in response.json()["detail"]


def test_07_adversarial_cross_transaction_signal_mismatch_fails_closed() -> None:
    """7. Mandatory Security Test: Cross-transaction signal in request causes 400 Bad Request."""
    other_tx_sig = _make_signal(score=10.0, tx_id="other_tx_99")
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [other_tx_sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Transaction ID mismatch" in response.json()["detail"]


def test_08_high_risk_score_produces_block() -> None:
    """8. Test high composite risk score produces BLOCK decision."""
    sig = _make_signal(score=85.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["decision"] == "BLOCK"
    assert data["risk_band"] == "HIGH_RISK_BAND"


def test_09_medium_risk_score_produces_review() -> None:
    """9. Test medium composite risk score produces REVIEW decision."""
    sig = _make_signal(score=50.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["decision"] == "REVIEW"
    assert data["risk_band"] == "MEDIUM_RISK_BAND"


def test_10_policy_deny_overrides_to_block() -> None:
    """10. Test Policy DENY signal produces BLOCK decision regardless of low score."""
    fraud_sig = _make_signal(sig_type=RiskSignalType.FRAUDGUARD, score=5.0)
    policy_sig = RiskSignal(
        signal_id=uuid.uuid4(),
        signal_type=RiskSignalType.POLICY,
        source="policy",
        score=None,
        score_unit=RiskScoreUnit.DECISION,
        normalized_score=None,
        confidence=1.0,
        decision="DENY",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
        tenant_id=TEST_TENANT_ID,
        agent_id=TEST_AGENT_ID,
        transaction_id=TEST_TX_ID,
        source_version="1.0.0",
        source_fingerprint="s1" * 32,
        availability=True,
        cold_start=False,
        metadata={
            "policy_decision": "DENY",
            "policy_decision_code": "SPENDING_LIMIT_EXCEEDED",
        },
    )

    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [fraud_sig.model_dump(mode="json"), policy_sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["decision"] == "BLOCK"
    assert data["policy_precedence"] == "DENY"


def test_11_audit_not_found_returns_404() -> None:
    """11. Test requesting nonexistent audit event returns 404 Not Found."""
    random_id = uuid.uuid4()
    response = client.get(f"/api/v1/risk-decisions/audit/{random_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert f"Decision audit event '{random_id}' not found." in response.json()["detail"]


def test_12_no_payment_execution_endpoints_or_razorpay_fields() -> None:
    """12. Security Test: No Razorpay or payment execution parameters exist in API response."""
    sig = _make_signal(score=10.0)
    payload = {
        "agent_id": str(TEST_AGENT_ID),
        "transaction_id": TEST_TX_ID,
        "signals": [sig.model_dump(mode="json")],
        "context_metadata": {},
    }

    response = client.post("/api/v1/risk-decisions/evaluate", json=payload)
    assert response.status_code == status.HTTP_200_OK
    dumped_json = response.text

    assert "razorpay" not in dumped_json.lower()
    assert "checkout_session" not in dumped_json.lower()
    assert "order_id" not in dumped_json.lower()
