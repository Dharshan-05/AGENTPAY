# AGENTGUARD Architecture Specification: Phase 193 — Merchant Restriction Engine

## Overview
Phase 193 implements `MerchantRestrictionService`, resolving merchant restrictions against existing `Merchant` ORM entities.

## Architecture & Tenant Boundary Rules
- **Model & Service Reuse**: Reuses existing `Merchant` ORM model ([`app/infrastructure/database/models/merchant.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/merchant.py)). Zero duplicate models.
- **Tenant Scope Enforcement**: Resolves merchant within `tenant_id` boundary. Missing or cross-tenant merchants raise `MerchantNotFoundError` (IDOR-safe 404 anti-enumeration).
- **Merchant Lifecycle Check**: Inactive, suspended, or archived merchants (`status != "active"`) return `DENIED` with `MERCHANT_INACTIVE`.
- **Precedence**: Denylist `DENY` > Allowlist `ALLOW`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
