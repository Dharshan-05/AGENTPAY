"""Unit tests for Phase 018 Global Error Handling exception taxonomy and safety."""

import json
import logging

import pytest

from app.application.exceptions import (
    ApplicationConflictError,
    ApplicationError,
    UseCaseError,
)
from app.core.logging import configure_logging
from app.domain.exceptions import (
    BusinessRuleViolationError,
    DomainError,
    EntityNotFoundError,
    InvalidStateError,
)
from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode
from app.exceptions.config_exceptions import ConfigurationError
from app.infrastructure.exceptions import (
    CacheError,
    DatabaseError,
    ExternalServiceError,
    InfrastructureError,
)


def test_base_agentpay_error_defaults() -> None:
    """Verify base AgentPayError initialization defaults."""
    err = AgentPayError()

    assert err.message == "An internal error occurred."
    assert err.code == ErrorCode.INTERNAL_ERROR
    assert err.details is None
    assert err.internal_message is None
    assert str(err) == "An internal error occurred."
    expected_repr = "AgentPayError(code='INTERNAL_ERROR', message='An internal error occurred.')"
    assert repr(err) == expected_repr


def test_error_codes_enum_stability() -> None:
    """Verify ErrorCode enum constants match expected machine-readable codes."""
    assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"
    assert ErrorCode.RESOURCE_NOT_FOUND.value == "RESOURCE_NOT_FOUND"
    assert ErrorCode.RESOURCE_CONFLICT.value == "RESOURCE_CONFLICT"
    assert ErrorCode.INVALID_CONFIGURATION.value == "INVALID_CONFIGURATION"
    assert ErrorCode.DOMAIN_ERROR.value == "DOMAIN_ERROR"
    assert ErrorCode.APPLICATION_ERROR.value == "APPLICATION_ERROR"
    assert ErrorCode.INFRASTRUCTURE_ERROR.value == "INFRASTRUCTURE_ERROR"
    assert ErrorCode.SERVICE_UNAVAILABLE.value == "SERVICE_UNAVAILABLE"


def test_domain_exceptions_hierarchy() -> None:
    """Verify domain exceptions inherit from DomainError and AgentPayError."""
    domain_err = DomainError("Domain rule failed")
    not_found = EntityNotFoundError("Account entity missing")
    rule_violation = BusinessRuleViolationError("Insufficient balance")
    invalid_state = InvalidStateError("Account is suspended")

    assert isinstance(domain_err, AgentPayError)
    assert isinstance(not_found, DomainError)
    assert not_found.code == ErrorCode.RESOURCE_NOT_FOUND

    assert isinstance(rule_violation, DomainError)
    assert rule_violation.code == ErrorCode.DOMAIN_ERROR

    assert isinstance(invalid_state, DomainError)
    assert invalid_state.code == ErrorCode.DOMAIN_ERROR


def test_application_exceptions_hierarchy() -> None:
    """Verify application exceptions inherit from ApplicationError and AgentPayError."""
    app_err = ApplicationError("Use case failed")
    use_case_err = UseCaseError("Payment execution failed")
    conflict_err = ApplicationConflictError("Transaction ID already exists")

    assert isinstance(app_err, AgentPayError)
    assert isinstance(use_case_err, ApplicationError)
    assert use_case_err.code == ErrorCode.APPLICATION_ERROR

    assert isinstance(conflict_err, ApplicationError)
    assert conflict_err.code == ErrorCode.RESOURCE_CONFLICT


def test_infrastructure_exceptions_hierarchy() -> None:
    """Verify infrastructure exceptions inherit from InfrastructureError and AgentPayError."""
    infra_err = InfrastructureError("Adapter failure")
    db_err = DatabaseError("Database query execution failed")
    cache_err = CacheError("Redis connection lost")
    ext_err = ExternalServiceError("Payment gateway gateway error")

    assert isinstance(infra_err, AgentPayError)
    assert isinstance(db_err, InfrastructureError)
    assert db_err.code == ErrorCode.INFRASTRUCTURE_ERROR

    assert isinstance(cache_err, InfrastructureError)
    assert cache_err.code == ErrorCode.INFRASTRUCTURE_ERROR

    assert isinstance(ext_err, InfrastructureError)
    assert ext_err.code == ErrorCode.SERVICE_UNAVAILABLE


def test_configuration_exception() -> None:
    """Verify ConfigurationError assigns INVALID_CONFIGURATION code."""
    config_err = ConfigurationError("SECRET_KEY length invalid")

    assert isinstance(config_err, AgentPayError)
    assert config_err.code == ErrorCode.INVALID_CONFIGURATION
    assert str(config_err) == "SECRET_KEY length invalid"


def test_public_message_separation() -> None:
    """Verify str(err) returns public safe message without internal details."""
    msg = "Database host db-primary.internal timed out on table account_id=123"
    err = AgentPayError(
        message="Resource not found.",
        code=ErrorCode.RESOURCE_NOT_FOUND,
        internal_message=msg,
    )

    assert str(err) == "Resource not found."
    assert "db-primary" not in str(err)
    assert err.internal_message == msg


def test_exception_chaining() -> None:
    """Verify Python exception chaining via from cause preserves original cause."""
    cause = RuntimeError("Raw socket timeout error")
    err = DatabaseError("Database unavailable", cause=cause)

    assert err.__cause__ is cause
    assert str(err.__cause__) == "Raw socket timeout error"


def test_secret_sanitization_in_details() -> None:
    """Verify sensitive keys in exception details dictionary are redacted."""
    details = {
        "account_id": "ACC_1001",
        "password": "SUPER_FAKE_SECRET_PASS_123",
        "api_key": "SUPER_FAKE_API_KEY_456",
    }
    err = AgentPayError(message="Operation failed", details=details)

    assert err.details is not None
    assert err.details["account_id"] == "ACC_1001"
    assert err.details["password"] == "[REDACTED]"
    assert err.details["api_key"] == "[REDACTED]"


def test_exception_structured_logging_compatibility(caplog: pytest.LogCaptureFixture) -> None:
    """Verify exceptions logged with Phase 017 structured logger produce valid JSON logs."""
    configure_logging()
    logger = logging.getLogger("agentpay.exceptions")

    try:
        raise EntityNotFoundError("Target account entity missing")
    except EntityNotFoundError as exc:
        with caplog.at_level(logging.ERROR):
            logger.exception("Failed to process entity", extra={"error_code": exc.code.value})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    from app.core.logging import JSONFormatter

    formatted_json = JSONFormatter().format(record)
    parsed = json.loads(formatted_json)

    assert parsed["level"] == "ERROR"
    assert parsed["logger"] == "agentpay.exceptions"
    assert "Failed to process entity" in parsed["message"]
    assert parsed["exception"]["type"] == "EntityNotFoundError"
    assert "Target account entity missing" in parsed["exception"]["message"]
    assert parsed.get("error_code") == "RESOURCE_NOT_FOUND"
