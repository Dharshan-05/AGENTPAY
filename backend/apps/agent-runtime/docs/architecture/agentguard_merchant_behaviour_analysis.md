# AGENTGUARD Architecture Specification: Phase 204 — Merchant Behaviour Analysis

## Overview
Phase 204 implements `MerchantBehaviourAnalysisService`, evaluating agent purchasing patterns for specific merchants.

## Architecture & Analysis Model
- **Familiarity Levels**: `FAMILIAR`, `UNFAMILIAR`, `FIRST_SEEN`, `INSUFFICIENT_DATA`.
- **Metrics**: Merchant transaction count, total amount (`Decimal`), average transaction amount, merchant transaction share ratio.
- **Tenant Isolation**: Queries strictly enforce `tenant_id` AND `agent_id` AND `merchant_id`.
- **Integration**: Advisory security signal integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
