# 08 — Role-Based Access Control (RBAC) Verification

## 1. Role Capabilities & Route Access Matrix

| Role | Permitted Routes | Denied Routes | Action on Unauthorized Access | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADMIN / OWNER** | All 14 Routes (`/agent-pay`, `/settings`, etc.) | None | Full Access Granted | **VERIFIED** |
| **ACCOUNTANT** | `/settlements`, `/settlements/reconciliation` | `/risk/investigations`, `/settings` | Redirected / Gate Blocked | **VERIFIED** |
| **SECOPS** | `/risk`, `/risk/investigations/[id]`, `/ai-insights` | `/settlements/reconciliation` | Redirected / Gate Blocked | **VERIFIED** |
| **SUPPORT** | `/payments/transactions`, `/payments/refunds` | `/settings`, `/agents/[id]` | Redirected / Gate Blocked | **VERIFIED** |
