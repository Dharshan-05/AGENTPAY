# AGENTGUARD Architecture Specification: Phase 200 — Behaviour Tracking

## Overview
Phase 200 implements `BehaviourTrackingService`, establishing a deterministic activity tracking subsystem for AGENTGUARD.

## Architecture & Data Sources
- **Authoritative Data Sources**: Queries authoritative historical activity from existing ORM entities (`PaymentOrder`, `ToolExecutionAudit`, etc.).
- **Normalized Event Model (`BehaviourEvent`)**: `event_id`, `tenant_id`, `agent_id`, `event_type`, `occurred_at`, `amount` (`Decimal`), `currency`, `merchant_id`, `category`, `status`, `outcome` (`SUCCESS`, `FAILED`).
- **Tenant Isolation**: Queries strictly enforce `tenant_id == tenant_id` AND `agent_id == agent_id`.
- **Bounded Pagination**: Queries enforce pagination bounds (max limit 100).
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
