"""Unit & Mandatory Security Tests for Risk Weight Configuration (Phase 275)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.risk_weights import DEFAULT_GOVERNED_WEIGHTS, RiskWeightService
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskSignalType,
    RiskWeightConfiguration,
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


def test_01_valid_default_weight_configuration() -> None:
    """1. Test default governed weight configuration initialization and validation."""
    ctx = _make_context()
    service = RiskWeightService()

    config = service.get_weight_configuration(context=ctx)

    assert config.configuration_version == "1.0.0"
    assert config.weights[RiskSignalType.FRAUDGUARD.value] == Decimal("2.0")
    assert RiskSignalType.POLICY.value not in config.weights
    assert len(config.compute_hash()) == 64


def test_02_policy_signal_weight_rejection() -> None:
    """2. Mandatory Absolute Rule Test: POLICY signal cannot be assigned advisory weights."""
    service = RiskWeightService()

    invalid_weights = dict(DEFAULT_GOVERNED_WEIGHTS)
    invalid_weights[RiskSignalType.POLICY.value] = Decimal("1.0")

    invalid_config = RiskWeightConfiguration(
        weights=invalid_weights,
    )

    with pytest.raises(ValueError, match="POLICY signal cannot be assigned an advisory weight"):
        service.validate_configuration(invalid_config)


def test_03_negative_weight_rejection() -> None:
    """3. Mandatory Security Test: Negative or zero weight fails closed."""
    service = RiskWeightService()

    invalid_weights = dict(DEFAULT_GOVERNED_WEIGHTS)
    invalid_weights[RiskSignalType.BEHAVIOUR.value] = Decimal("-1.0")

    invalid_config = RiskWeightConfiguration(weights=invalid_weights)

    with pytest.raises(ValueError, match="strictly positive"):
        service.validate_configuration(invalid_config)


def test_04_nan_weight_rejection() -> None:
    """4. Mandatory Security Test: NaN weight fails closed."""
    service = RiskWeightService()

    with pytest.raises(ValueError):
        invalid_config = RiskWeightConfiguration.model_construct(
            weights={RiskSignalType.FRAUDGUARD.value: Decimal("nan")},
            configuration_version="1.0.0",
        )
        service.validate_configuration(invalid_config)


def test_05_unknown_signal_type_rejection() -> None:
    """5. Mandatory Security Test: Unknown signal type in weights fails closed."""
    service = RiskWeightService()

    invalid_config = RiskWeightConfiguration(
        weights={"UNKNOWN_SIGNAL_TYPE": Decimal("1.0")},
    )

    with pytest.raises(ValueError, match="Unknown signal type"):
        service.validate_configuration(invalid_config)


def test_06_future_effective_date_rejection() -> None:
    """6. Mandatory Temporal Security Test: Future effective_from config fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_from = datetime(2030, 1, 1, tzinfo=UTC)
    service = RiskWeightService()

    future_config = RiskWeightConfiguration(
        weights=DEFAULT_GOVERNED_WEIGHTS,
        effective_from=future_from,
    )

    with pytest.raises(ValueError, match="is in the future relative to prediction timestamp"):
        service.validate_configuration(future_config, context=ctx)


def test_07_tenant_mismatch_weight_config_rejection() -> None:
    """7. Mandatory Security Test: Tenant mismatch in weight configuration fails closed."""
    ctx = _make_context()
    service = RiskWeightService()

    other_tenant = uuid.uuid4()
    tenant_config = RiskWeightConfiguration(
        tenant_id=other_tenant,  # Cross-tenant config attack!
        weights=DEFAULT_GOVERNED_WEIGHTS,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch in weight config"):
        service.validate_configuration(tenant_config, context=ctx)


def test_08_deterministic_weight_config_hash() -> None:
    """8. Test configuration hash determinism across identical weight structures."""
    cfg1 = RiskWeightConfiguration(weights=DEFAULT_GOVERNED_WEIGHTS)
    cfg2 = RiskWeightConfiguration(weights=DEFAULT_GOVERNED_WEIGHTS)

    assert cfg1.compute_hash() == cfg2.compute_hash()
