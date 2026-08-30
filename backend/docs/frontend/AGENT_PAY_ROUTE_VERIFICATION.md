# AGENTPAY — Route & Page Verification Matrix

## 1. Route Execution Verification Table

| Route | Page Name | Resolves | Layout & Nav | RBAC Target | Responsive Rating | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | Root Redirect | ✅ Yes | Redirects to `/agent-pay` | Public / All | 100% | **PASS** |
| `/agent-pay` | Executive Overview | ✅ Yes | `<DashboardLayout />` | Admin, Owner | 100% | **PASS** |
| `/payments/transactions` | Payment Operations | ✅ Yes | `<DashboardLayout />` | Admin, Support | 100% | **PASS** |
| `/payments/transactions/[id]` | Transaction Detail | ✅ Yes | `<DashboardLayout />` | Admin, Support | 100% | **PASS** |
| `/payments/refunds` | Refund Claims | ✅ Yes | `<DashboardLayout />` | Admin, Support | 100% | **PASS** |
| `/agents` | Agent Fleet Manager | ✅ Yes | `<DashboardLayout />` | Admin, Owner | 100% | **PASS** |
| `/agents/[id]` | Agent Profile & Trust | ✅ Yes | `<DashboardLayout />` | Admin, Owner | 100% | **PASS** |
| `/merchants` | Merchant Operations | ✅ Yes | `<DashboardLayout />` | Admin, Merchant | 100% | **PASS** |
| `/settlements` | Settlement Ledger | ✅ Yes | `<DashboardLayout />` | Admin, Accountant | 100% | **PASS** |
| `/settlements/reconciliation` | Reconciliation | ✅ Yes | `<DashboardLayout />` | Admin, Accountant | 100% | **PASS** |
| `/risk` | Threat Center | ✅ Yes | `<DashboardLayout />` | Admin, SecOps | 100% | **PASS** |
| `/risk/investigations/[id]` | Risk Investigation | ✅ Yes | `<DashboardLayout />` | Admin, SecOps | 100% | **PASS** |
| `/analytics` | Performance Analytics | ✅ Yes | `<DashboardLayout />` | Admin, Owner | 100% | **PASS** |
| `/ai-insights` | AI Intelligence Hub | ✅ Yes | `<DashboardLayout />` | Admin, SecOps | 100% | **PASS** |

---

## 2. Navigation & Breadcrumb Behavior

* **Sidebar Deep Links**: All 8 primary navigation items in `Sidebar.tsx` correctly highlight the active route and preserve tenant context.
* **Breadcrumb Back Navigation**: Every detail view (`/payments/transactions/[id]`, `/agents/[id]`, `/risk/investigations/[id]`, `/settlements/reconciliation`) includes clickable breadcrumb links and `<ArrowLeft />` back buttons.
* **Dynamic Parameter Resolution**: `useParams()` correctly extracts route parameters (`payment_id`, `agent_id`, `alert_id`) and fallbacks gracefully if unmatched.
