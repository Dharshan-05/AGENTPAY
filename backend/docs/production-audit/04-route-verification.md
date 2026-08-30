# 04 — Router Audit & Route Navigation Topology

## 1. Verified App Router Entrypoints

| Route Path | Component File | Direct URL Access | Refresh Safe | RBAC Scope | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | `apps/web/src/app/page.tsx` | ✅ Yes | ✅ Yes | All Users | **PASS** |
| `/agent-pay` | `apps/web/src/app/(dashboard)/agent-pay/page.tsx` | ✅ Yes | ✅ Yes | Admin, Owner | **PASS** |
| `/payments/transactions` | `apps/web/src/app/(dashboard)/payments/transactions/page.tsx` | ✅ Yes | ✅ Yes | Admin, Support | **PASS** |
| `/payments/transactions/[id]` | `apps/web/src/app/(dashboard)/payments/transactions/[id]/page.tsx` | ✅ Yes | ✅ Yes | Admin, Support | **PASS** |
| `/payments/refunds` | `apps/web/src/app/(dashboard)/payments/refunds/page.tsx` | ✅ Yes | ✅ Yes | Admin, Support | **PASS** |
| `/agents` | `apps/web/src/app/(dashboard)/agents/page.tsx` | ✅ Yes | ✅ Yes | Admin, Owner | **PASS** |
| `/agents/[id]` | `apps/web/src/app/(dashboard)/agents/[id]/page.tsx` | ✅ Yes | ✅ Yes | Admin, Owner | **PASS** |
| `/merchants` | `apps/web/src/app/(dashboard)/merchants/page.tsx` | ✅ Yes | ✅ Yes | Admin, Merchant | **PASS** |
| `/settlements` | `apps/web/src/app/(dashboard)/settlements/page.tsx` | ✅ Yes | ✅ Yes | Admin, Accountant | **PASS** |
| `/settlements/reconciliation` | `apps/web/src/app/(dashboard)/settlements/reconciliation/page.tsx` | ✅ Yes | ✅ Yes | Admin, Accountant | **PASS** |
| `/risk` | `apps/web/src/app/(dashboard)/risk/page.tsx` | ✅ Yes | ✅ Yes | Admin, SecOps | **PASS** |
| `/risk/investigations/[id]` | `apps/web/src/app/(dashboard)/risk/investigations/[id]/page.tsx` | ✅ Yes | ✅ Yes | Admin, SecOps | **PASS** |
| `/analytics` | `apps/web/src/app/(dashboard)/analytics/page.tsx` | ✅ Yes | ✅ Yes | Admin, Owner | **PASS** |
| `/ai-insights` | `apps/web/src/app/(dashboard)/ai-insights/page.tsx` | ✅ Yes | ✅ Yes | Admin, SecOps | **PASS** |
| `/settings` | `apps/web/src/app/(dashboard)/settings/page.tsx` | ✅ Yes | ✅ Yes | Admin, Owner | **PASS** |

* **Dead Routes Detected**: 0
* **Unreachable Routes**: 0
* **Duplicate Routes**: 0
