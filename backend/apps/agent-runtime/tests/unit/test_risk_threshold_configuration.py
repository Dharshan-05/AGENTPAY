"""Unit & Mandatory Security Tests for Risk Threshold Configuration (Phase 276)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.risk_thresholds import RiskThresholdService
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskThresholdConfiguration,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_001",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_01_valid_threshold_configuration() -> None:
    """1. Test valid governed threshold configuration initialization and validation."""
    service = RiskThresholdService()

    config = service.default_config
    assert config.allow_upper_bound == Decimal("30.0")
    assert config.review_upper_bound == Decimal("70.0")
    assert len(config.compute_hash()) == 64


def test_02_negative_threshold_rejection() -> None:
    """2. Mandatory Security Test: Negative threshold fails closed."""
    service = RiskThresholdService()

    invalid_config = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("-10.0"),  # Negative bound!
        review_upper_bound=Decimal("70.0"),
    )

    with pytest.raises(ValueError, match="out of valid range"):
        service.validate_configuration(invalid_config)


def test_03_threshold_above_100_rejection() -> None:
    """3. Mandatory Security Test: Threshold > 100 fails closed."""
    service = RiskThresholdService()

    invalid_config = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("30.0"),
        review_upper_bound=Decimal("110.0"),  # > 100 bound!
    )

    with pytest.raises(ValueError, match="out of valid range"):
        service.validate_configuration(invalid_config)


def test_04_nan_threshold_rejection() -> None:
    """4. Mandatory Security Test: NaN threshold fails closed."""
    service = RiskThresholdService()

    with pytest.raises(ValueError):
        invalid_config = RiskThresholdConfiguration.model_construct(
            allow_upper_bound=Decimal("nan"),
            review_upper_bound=Decimal("70.0"),
        )
        service.validate_configuration(invalid_config)


def test_05_inverted_thresholds_rejection() -> None:
    """5. Mandatory Security Test: Inverted bounds (allow > review) fails closed."""
    service = RiskThresholdService()

    inverted_config = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("80.0"),  # Inverted!
        review_upper_bound=Decimal("40.0"),
    )

    with pytest.raises(ValueError, match="Inverted threshold bounds"):
        service.validate_configuration(inverted_config)


def test_06_future_threshold_effective_date_rejection() -> None:
    """6. Mandatory Temporal Security Test: Future effective_from fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_from = datetime(2030, 1, 1, tzinfo=UTC)
    service = RiskThresholdService()

    future_config = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("30.0"),
        review_upper_bound=Decimal("70.0"),
        effective_from=future_from,
    )

    with pytest.raises(ValueError, match="is in the future relative to prediction timestamp"):
        service.validate_configuration(future_config, context=ctx)


def test_07_tenant_mismatch_threshold_config_rejection() -> None:
    """7. Mandatory Security Test: Tenant mismatch in threshold configuration fails closed."""
    ctx = _make_context()
    service = RiskThresholdService()

    other_tenant = uuid.uuid4()
    tenant_config = RiskThresholdConfiguration(
        tenant_id=other_tenant,  # Cross-tenant config attack!
        allow_upper_bound=Decimal("30.0"),
        review_upper_bound=Decimal("70.0"),
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch in threshold config"):
        service.validate_configuration(tenant_config, context=ctx)


def test_08_deterministic_threshold_config_hash() -> None:
    """8. Test threshold configuration hash determinism."""
    cfg1 = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("30.0"), review_upper_bound=Decimal("70.0")
    )
    cfg2 = RiskThresholdConfiguration(
        allow_upper_bound=Decimal("30.0"), review_upper_bound=Decimal("70.0")
    )

    assert cfg1.compute_hash() == cfg2.compute_hash()
