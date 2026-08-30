# AGENTGUARD Architecture Specification: Phase 205 — Category Behaviour Analysis

## Overview
Phase 205 implements `CategoryBehaviourAnalysisService`, evaluating agent purchasing patterns across product category dimensions.

## Architecture & Analysis Model
- **Normalization & Hierarchy**: Strips whitespace, lowercases, and supports dot-separated hierarchical category paths (e.g., `electronics.mobile`).
- **Familiarity Levels**: `FAMILIAR`, `UNFAMILIAR`, `FIRST_SEEN`, `INSUFFICIENT_DATA`.
- **Metrics**: Category transaction count, total amount (`Decimal`), average transaction amount, category transaction share ratio.
- **Integration**: Advisory security signal integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
