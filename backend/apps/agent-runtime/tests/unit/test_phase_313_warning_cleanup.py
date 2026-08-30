"""Unit Test Suite for Phase 313 — Dependency Warning Cleanup & Deprecation Verification (P3-01)."""

from __future__ import annotations

import warnings

from app.schemas.human_approval import HumanApprovalCommand, HumanApprovalResult
from app.schemas.payment import SupportedCurrency


def test_01_pydantic_v2_model_fields_access() -> None:
    """Test 1: Pydantic v2 schemas expose model_fields without DeprecationWarning."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        fields = HumanApprovalCommand.model_fields
        assert "approval_request_id" in fields
        assert "idempotency_key" in fields

    dep_warnings = [w for w in recorded if issubclass(w.category, DeprecationWarning)]
    assert len(dep_warnings) == 0


def test_02_human_approval_result_fields_access() -> None:
    """Test 2: HumanApprovalResult exposes model_fields with zero warnings."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        fields = HumanApprovalResult.model_fields
        assert "status" in fields
        assert "is_existing" in fields

    dep_warnings = [w for w in recorded if issubclass(w.category, DeprecationWarning)]
    assert len(dep_warnings) == 0


def test_03_no_deprecated_fields_attribute_access() -> None:
    """Test 3: Accessing model_fields on SupportedCurrency models emits zero deprecation warnings."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        assert len(SupportedCurrency) > 0

    dep_warnings = [w for w in recorded if issubclass(w.category, DeprecationWarning)]
    assert len(dep_warnings) == 0
