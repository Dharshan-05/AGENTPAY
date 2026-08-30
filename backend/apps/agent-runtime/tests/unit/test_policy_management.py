"""Unit Tests for Policy Management Subsystem (Phase 185)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.schemas.policies import PolicyCreateRequest, PolicyResponse


def test_01_policy_create_request_validation() -> None:
    """1. Test PolicyCreateRequest model validation."""
    req = PolicyCreateRequest(
        name="Global Spending Limit",
        description="Limits single transaction spending to 500 USD",
        policy_type="spending",
        priority=200,
        enforcement_mode="enforce",
        configuration={"max_transaction_amount": "500.00"},
    )
    assert req.name == "Global Spending Limit"
    assert req.priority == 200
    assert req.configuration["max_transaction_amount"] == "500.00"


def test_02_policy_response_serialization() -> None:
    """2. Test PolicyResponse data structure."""
    policy_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    now = datetime.now(UTC)

    resp = PolicyResponse(
        id=policy_id,
        tenant_id=tenant_id,
        name="Merchant Restriction",
        slug="merchant-restriction",
        description="Restricts unauthorized merchants",
        status="active",
        policy_type="merchant",
        priority=100,
        enforcement_mode="block",
        version=1,
        starts_at=now,
        ends_at=None,
        configuration={},
        created_at=now,
        updated_at=now,
    )

    assert resp.id == policy_id
    assert resp.status == "active"
    assert resp.enforcement_mode == "block"
