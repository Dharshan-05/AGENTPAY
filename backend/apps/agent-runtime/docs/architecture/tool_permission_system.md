# AGENTPAY Architecture Specification: Phase 158 — Tool Permission System

## Overview
Phase 158 transforms tool authorization into a mandatory, policy-driven permission gate in AGENTPAY.

## Decision Model
```
Agent Request ──> Tool Permission Engine ──> Decision
                                               ├── ALLOW (Low risk / authorized)
                                               ├── DENY (Unauthorized / fail-closed)
                                               └── REQUIRE_APPROVAL (High risk / financial > $50)
```

## Security Rules
- **Fail-Closed Default**: Any ambiguous context, missing tool status, or missing permission defaults to `DENY`.
- **RBAC Permission Gate**: Enforces canonical `tools:execute` and `tools:read` permissions resolved from user and agent roles.
- **Risk & Financial Thresholds**: High/critical risk tools or operations exceeding $50.00 require human approval (Phase 162).
