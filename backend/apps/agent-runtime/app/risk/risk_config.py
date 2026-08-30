"""Risk Engine Configuration Module (Phase 266)."""

from __future__ import annotations

import hashlib
import json
import logging

from app.schemas.risk_engine import RiskEngineConfig

logger = logging.getLogger("agentpay.risk.config")


def compute_configuration_hash(config: RiskEngineConfig) -> str:
    """Compute canonical SHA-256 fingerprint hash for RiskEngineConfig."""
    payload = {
        "engine_version": config.engine_version,
        "configuration_version": config.configuration_version,
        "strict_identity_binding": config.strict_identity_binding,
        "strict_point_in_time": config.strict_point_in_time,
        "reject_target_leakage": config.reject_target_leakage,
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
