# AGENTGUARD Architecture Specification: Phase 201 — Behaviour Baseline

## Overview
Phase 201 implements `BehaviourBaselineService`, calculating an agent's normal operational baseline from historical activity.

## Statistical Model & Cold-Start Rules
- **Minimum Observation Rule**: If observation count < 5, baseline returns `baseline_available = False` and `state = "COLD_START"`.
- **Financial Precision**: All monetary aggregations (`total_amount`, `average_amount`, `min_amount`, `max_amount`) use Python `Decimal` exclusively.
- **Top Metrics**: Tracks frequent merchants, frequent categories, and frequent currencies.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
