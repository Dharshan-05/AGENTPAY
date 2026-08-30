# AGENTGUARD Architecture Specification: Phase 203 — Velocity Detection

## Overview
Phase 203 implements `VelocityDetectionService`, establishing a deterministic velocity analysis subsystem for AGENTGUARD.

## Architecture & Calculation Model
- **Data Source**: Reuses authoritative `PaymentOrder` ORM records.
- **Velocity Metrics**: Transaction count, total monetary amount (`Decimal`), transactions per minute, transactions per hour.
- **Tenant Isolation**: Queries strictly enforce `tenant_id == tenant_id` AND `agent_id == agent_id`.
- **Bounded Time Windows**: Configurable analysis window (default 60 minutes, max 1440 minutes / 24 hours).
- **Severity Classification**: `NORMAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `INSUFFICIENT_DATA`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
