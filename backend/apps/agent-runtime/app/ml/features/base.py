"""Core Feature Engineering Framework Base Abstractions (Phase 221)."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any


class FeatureType(enum.Enum):
    """Supported feature data types (Phase 221)."""

    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    ARRAY = "ARRAY"


class FeatureSecurityClassification(enum.Enum):
    """Security classifications for feature access control (Phase 221)."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    SENSITIVE = "SENSITIVE"
    RESTRICTED = "RESTRICTED"


class FeatureCategory(enum.Enum):
    """Feature taxonomy classification (Phase 221)."""

    TRANSACTION = "TRANSACTION"
    BEHAVIOUR = "BEHAVIOUR"
    MERCHANT = "MERCHANT"
    VELOCITY = "VELOCITY"
    INTENT = "INTENT"
    POLICY = "POLICY"
    TRUST = "TRUST"
    RISK = "RISK"
    META = "META"


@dataclass(frozen=True)
class FeatureDefinition:
    """Typed feature definition specification contract (Phase 221)."""

    name: str
    feature_type: FeatureType
    source: str
    transformation_description: str
    feature_id: str = ""
    version: str = "1.0.0"
    owner: str = "fraudguard-team"
    category: FeatureCategory = FeatureCategory.META
    security_classification: FeatureSecurityClassification = FeatureSecurityClassification.INTERNAL
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    bounds: tuple[float | None, float | None] | None = None
    nullable: bool = True
    freshness_seconds: int = 3600
    default_value: Any = None

    def __post_init__(self) -> None:
        if not self.feature_id:
            object.__setattr__(self, "feature_id", f"{self.name}:{self.version}")


@dataclass
class FeatureValue:
    """Individual extracted feature value with provenance and lineage (Phase 221)."""

    definition: FeatureDefinition
    value: Any
    tenant_id: str
    agent_id: str | None = None
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert feature value to dictionary format preserving precision."""
        val = self.value
        if isinstance(val, Decimal):
            val = float(val)
        return {
            "name": self.definition.name,
            "feature_id": self.definition.feature_id,
            "value": val,
            "feature_type": self.definition.feature_type.value,
            "category": self.definition.category.value,
            "security_classification": self.definition.security_classification.value,
            "version": self.definition.version,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "computed_at": self.computed_at.isoformat(),
        }


class FeatureDependencyGraph:
    """Graph manager for detecting feature dependency cycles and missing links (Phase 221)."""

    def __init__(self) -> None:
        self.nodes: dict[str, FeatureDefinition] = {}

    def add_feature(self, definition: FeatureDefinition) -> None:
        """Add a feature node to the dependency graph."""
        self.nodes[definition.name] = definition

    def validate_dependencies(self) -> list[str]:
        """Validate feature dependencies for missing links or cycles."""
        issues: list[str] = []

        for name, feat in self.nodes.items():
            for dep in feat.dependencies:
                if dep not in self.nodes:
                    issues.append(f"Feature '{name}' depends on missing feature '{dep}'")

                # Direct cycle check
                if dep in self.nodes and name in self.nodes[dep].dependencies:
                    issues.append(f"Circular dependency detected between '{name}' and '{dep}'")

        return issues
