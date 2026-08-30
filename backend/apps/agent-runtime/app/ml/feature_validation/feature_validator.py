"""Feature Quality Gate & Validation (Phase 229)."""

from __future__ import annotations

import math
import uuid
from decimal import Decimal

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.features.base import FeatureValue
from app.schemas.ml_features import FeatureValidationResult, FeatureValidationViolation


class FeatureValidator:
    """Production Feature Quality Gate & Leakage Detection Engine (Phase 229)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()

    def validate_features(
        self,
        features: list[FeatureValue],
        expected_tenant_id: uuid.UUID | None = None,
    ) -> FeatureValidationResult:
        """Perform quality gate checks on feature vector with leakage & quality scoring (Phase 229)."""  # noqa: E501
        violations: list[FeatureValidationViolation] = []
        leakage_detected = False

        if not features:
            violations.append(
                FeatureValidationViolation(
                    feature_name="ALL",
                    code="EMPTY_FEATURE_SET",
                    message="Feature vector is empty.",
                    severity="ERROR",
                )
            )
            return FeatureValidationResult(
                valid=False,
                feature_count=0,
                quality_score=Decimal("0.00"),
                leakage_detected=False,
                violations=violations,
            )

        tenant_str = str(expected_tenant_id) if expected_tenant_id else None
        valid_feature_count = len(features)

        for f in features:
            fname = f.definition.name

            # 1. Tenant boundary leak check
            if tenant_str and f.tenant_id != tenant_str:
                violations.append(
                    FeatureValidationViolation(
                        feature_name=fname,
                        code="TENANT_LEAKAGE",
                        message=f"Feature tenant '{f.tenant_id}' mismatches expected '{tenant_str}'",  # noqa: E501
                        severity="FATAL",
                    )
                )
                leakage_detected = True
                valid_feature_count -= 1

            val = f.value

            # 2. Numerical validation (NaN, Infinity, bounds)
            if isinstance(val, float):
                if math.isnan(val):
                    violations.append(
                        FeatureValidationViolation(
                            feature_name=fname,
                            code="NAN_VALUE",
                            message=f"Feature {fname} contains NaN.",
                            severity="ERROR",
                        )
                    )
                    valid_feature_count -= 1
                elif math.isinf(val):
                    violations.append(
                        FeatureValidationViolation(
                            feature_name=fname,
                            code="INF_VALUE",
                            message=f"Feature {fname} contains Infinity.",
                            severity="ERROR",
                        )
                    )
                    valid_feature_count -= 1

                bounds = f.definition.bounds
                if bounds:
                    min_b, max_b = bounds
                    if min_b is not None and val < min_b:
                        violations.append(
                            FeatureValidationViolation(
                                feature_name=fname,
                                code="OUT_OF_BOUNDS_MIN",
                                message=f"Feature {fname} value {val} < min bound {min_b}",
                                severity="ERROR",
                            )
                        )
                    if max_b is not None and val > max_b:
                        violations.append(
                            FeatureValidationViolation(
                                feature_name=fname,
                                code="OUT_OF_BOUNDS_MAX",
                                message=f"Feature {fname} value {val} > max bound {max_b}",
                                severity="ERROR",
                            )
                        )

            # 3. Target leakage check (naming & metadata heuristic)
            if "label" in fname.lower() or "target" in fname.lower():
                violations.append(
                    FeatureValidationViolation(
                        feature_name=fname,
                        code="SUSPECTED_TARGET_LEAKAGE",
                        message=f"Feature name {fname} contains target keyword.",
                        severity="WARNING",
                    )
                )

        # Feature quality score calculation (0.00 to 1.00)
        quality_ratio = Decimal(str(round(max(0, valid_feature_count) / len(features), 2)))
        leakage_penalty = Decimal("0.50") if leakage_detected else Decimal("0.00")
        quality_score = max(Decimal("0.00"), quality_ratio - leakage_penalty)

        has_fatal_or_error = any(v.severity in ("ERROR", "FATAL") for v in violations)
        return FeatureValidationResult(
            valid=not has_fatal_or_error,
            feature_count=len(features),
            quality_score=quality_score,
            leakage_detected=leakage_detected,
            violations=violations,
        )
