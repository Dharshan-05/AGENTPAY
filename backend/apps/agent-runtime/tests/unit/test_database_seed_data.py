"""Unit Tests for Phase 078 Database Seed Engine."""

import pytest

from app.infrastructure.database.seeder import (
    SEED_AGENT_ID,
    SEED_MERCHANT_ID,
    SEED_ORDER_ID,
    SEED_PRODUCT_ID,
    SEED_TENANT_ID,
    SEED_TXN_ID,
    SEED_USER_ID,
    ProductionSeedingProhibitedError,
    verify_seed_environment,
)


def test_01_production_environment_rejection() -> None:
    """1. Verify seeding is strictly prohibited in production environments."""
    with pytest.raises(ProductionSeedingProhibitedError):
        verify_seed_environment("production")

    with pytest.raises(ProductionSeedingProhibitedError):
        verify_seed_environment("prod")

    with pytest.raises(ProductionSeedingProhibitedError):
        verify_seed_environment("live")


def test_02_allowed_environments() -> None:
    """2. Verify development, test, and demo environments are permitted."""
    assert verify_seed_environment("development") == "development"
    assert verify_seed_environment("test") == "test"
    assert verify_seed_environment("demo") == "demo"


def test_03_deterministic_seed_uuids() -> None:
    """3. Verify deterministic seed UUID namespace constants are valid UUIDs."""
    assert str(SEED_TENANT_ID) == "00000000-0000-4000-a000-000000000001"
    assert str(SEED_USER_ID) == "00000000-0000-4000-a000-000000000002"
    assert str(SEED_MERCHANT_ID) == "00000000-0000-4000-a000-000000000003"
    assert str(SEED_AGENT_ID) == "00000000-0000-4000-a000-000000000004"
    assert str(SEED_PRODUCT_ID) == "00000000-0000-4000-a000-000000000005"
    assert str(SEED_ORDER_ID) == "00000000-0000-4000-a000-000000000010"
    assert str(SEED_TXN_ID) == "00000000-0000-4000-a000-000000000011"
