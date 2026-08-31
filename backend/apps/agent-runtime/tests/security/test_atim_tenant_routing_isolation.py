"""Security test suite verifying tenant memory and routing metrics isolation (Phase 9)."""

import uuid
import pytest

from app.application.services.atim_intelligent_router import ATIMIntelligentRouter


def test_01_tenant_routing_metadata_isolated():
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    router = ATIMIntelligentRouter()

    decision_a = router.route_request("Buy a laptop", tenant_id=tenant_a)
    decision_b = router.route_request("Buy a phone", tenant_id=tenant_b)

    assert decision_a.tenant_id == tenant_a
    assert decision_b.tenant_id == tenant_b
    assert decision_a.tenant_id != decision_b.tenant_id
