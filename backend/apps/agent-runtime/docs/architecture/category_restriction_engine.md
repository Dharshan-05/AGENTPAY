# AGENTGUARD Architecture Specification: Phase 192 — Category Restriction Engine

## Overview
Phase 192 implements `CategoryRestrictionService`, enforcing category allowlists and denylists for agent transactions.

## Architecture & Normalization Semantics
- **Category Normalization**: Case and whitespace normalization (`category.strip().lower()`). Zero fuzzy matching, zero arbitrary regex execution.
- **Hierarchical Support**: Supports sub-category matching (e.g. `electronics.mobile` matches rule `electronics`).
- **Denylist Precedence**: Explicit `DENY` rules override allowlist rules.
- **Missing Category**: If category is missing and a restrictive allowlist is present, fails closed (`DENIED`, `CATEGORY_MISSING`).
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
