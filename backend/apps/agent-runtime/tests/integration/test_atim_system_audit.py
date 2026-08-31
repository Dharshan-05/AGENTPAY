"""Integration tests for ATIM Automated System Release Audit Engine (Phase 16 / Group 8)."""

import pytest

from app.application.services.atim_system_audit_service import ATIMSystemAuditService


def test_01_system_audit_scorecard_verifies_all_invariants():
    audit_service = ATIMSystemAuditService()
    scorecard = audit_service.run_system_audit()

    assert scorecard.status == "PASSED"
    assert scorecard.total_invariants_checked == 15
    assert scorecard.compliant_invariants_count == 15
    assert scorecard.tenant_isolation_verified is True
    assert scorecard.audit_lock_verified is True
    assert len(scorecard.invariants) == 15
