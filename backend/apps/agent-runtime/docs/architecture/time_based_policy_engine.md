# AGENTGUARD Architecture Specification: Phase 194 — Time-Based Policy Engine

## Overview
Phase 194 implements `TimeBasedPolicyService`, providing decision-only time-eligibility evaluation for security policies.

## Features & Timezone Safety
- **Window Types**: `ALWAYS_ACTIVE`, `DATE_RANGE`, `TIME_WINDOW`, `DAY_OF_WEEK`, `DATE_AND_TIME_WINDOW`.
- **Timezone Conversion**: Evaluates timestamps using Python `zoneinfo.ZoneInfo`. Converts UTC timestamps to requested IANA timezones (e.g., `America/New_York`). Invalid timezones fail closed (`INVALID_TIMEZONE`).
- **Midnight Crossing**: Supports overnight daily time windows (e.g. `22:00` to `06:00`).
- **Fail-Closed Semantics**: Unmatched days, expired date ranges, or invalid formats mark policies as ineligible (`is_eligible = False`).
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
