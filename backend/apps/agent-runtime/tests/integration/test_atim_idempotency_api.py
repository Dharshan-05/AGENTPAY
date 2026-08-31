"""Integration tests for ATIM Idempotency & Recovery REST APIs (Group 11)."""

import pytest


def test_01_idempotency_model_imports():
    from app.domain.governance.idempotency_models import IdempotencyState
    assert IdempotencyState.SUCCEEDED.value == "SUCCEEDED"
    assert IdempotencyState.PROCESSING.value == "PROCESSING"
