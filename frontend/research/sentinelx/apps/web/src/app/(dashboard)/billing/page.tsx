"use client"

import { useEffect, useState } from "react"
import {
  Users,
  Database,
  ShieldCheck,
  Crown,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Loader2,
  Download,
  Receipt,
  TrendingUp,
  BarChart3,
  AlertCircle,
  ExternalLink,
  Settings,
  Zap,
  FileText,
  Building2,
  Clock,
} from "lucide-react"
import { Badge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api"

type PlanId = keyof typeof PLANS

const PLANS = {
  trial: {
    id: "trial",
    name: "Trial",
    price: 9,
    yearlyPrice: 9,
    currency: "INR",
    interval: "one_time",
    features: {
      users: 5,
      aiRequests: 1000,
      storage: 1,
      compliancePacks: 1,
      prioritySupport: false,
      socDashboard: false,
      unlimitedAuditLogs: false,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: false,
    },
  },
  starter: {
    id: "starter",
    name: "Starter",
    price: 49,
    yearlyPrice: 490,
    currency: "INR",
    interval: "monthly",
    features: {
      users: 5,
      aiRequests: 10000,
      storage: 10,
      compliancePacks: 2,
      prioritySupport: false,
      socDashboard: false,
      unlimitedAuditLogs: false,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: false,
    },
  },
  professional: {
    id: "professional",
    name: "Professional",
    price: 149,
    yearlyPrice: 1490,
    currency: "INR",
    interval: "monthly",
    features: {
      users: 25,
      aiRequests: 100000,
      storage: 100,
      compliancePacks: 5,
      prioritySupport: true,
      socDashboard: true,
      unlimitedAuditLogs: true,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: true,
    },
  },
  enterprise: {
    id: "enterprise",
    name: "Enterprise",
    price: 499,
    yearlyPrice: 4990,
    currency: "INR",
    interval: "monthly",
    features: {
      users: -1,
      aiRequests: -1,
      storage: -1,
      compliancePacks: 5,
      prioritySupport: true,
      socDashboard: true,
      unlimitedAuditLogs: true,
      enterpriseSSO: true,
      apiAccess: true,
      customPolicies: true,
    },
  },
} as const

interface Subscription {
  id: string
  entity: string
  plan_id: string
  customer_id: string
  status: string
  current_start: number
  current_end: number
  ended_at: number | null
  quantity: number
  notes: Record<string, unknown>
  charge_at: number
  start_at: number
  end_at: number
  auth_attempts: number
  total_count: number
  paid_count: number
  customer_notify: boolean
  created_at: number
  expire_by: number | null
  remaining_count: number
}

interface Invoice {
  id: string
  entity: string
  amount: number
  amount_paid: number
  amount_due: number
  currency: string
  status: string
  receipt: string
  description: string
  customer_id: string
  date: number
  due_date: number
  paid_at: number | null
  notes: Record<string, unknown>
  line_items: Array<{
    name: string
    description: string
    amount: number
    currency: string
    quantity: number
  }>
}

interface UsageData {
  current: {
    protectedPrompts: number
    llmCalls: number
    storageUsed: number
    incidents: number
    reportsGenerated: number
    complianceChecks: number
  }
  limits: {
    protectedPrompts: number
    llmCalls: number
    storage: number
    incidents: number
    reportsGenerated: number
    complianceChecks: number
  }
  history: Array<{
    month: string
    protectedPrompts: number
    llmCalls: number
    storage: number
    incidents: number
    reports: number
    checks: number
  }>
  forecast: {
    nextMonth: {
      protectedPrompts: number
      llmCalls: number
      storage: number
      incidents: number
      reports: number
      checks: number
    }
  }
}

interface AnalyticsData {
  mrr: number
  arr: number
  activeSubscriptions: number
  trialUsers: number
  enterpriseCustomers: number
  paymentSuccessRate: number
  refundRate: number
  monthlyGrowth: number
  revenueHistory: Array<{
    month: string
    revenue: number
    subscriptions: number
  }>
}
export default function BillingPage() {
  const { data: session } = useSession()
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly")
  const [currentPlan, setCurrentPlan] = useState<PlanId>("trial")
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [usage, setUsage] = useState<UsageData | null>(null)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchBillingData()
    const interval = setInterval(fetchBillingData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchBillingData = async () => {
    try {
      const [subRes, invRes, usageRes, analyticsRes] = await Promise.allSettled([
        api.subscription(),
        api.invoices(),
        api.billingUsage(),
        api.billingAnalytics(),
      ])

      if (subRes.status === "fulfilled" && subRes.value?.subscription) {
        setSubscription(subRes.value.subscription)
        const planMap: Record<string, PlanId> = {
          "plan_trial": "trial",
          "plan_starter": "starter",
          "plan_professional": "professional",
          "plan_enterprise": "enterprise",
        }
        setCurrentPlan(planMap[subRes.value.subscription.plan_id] ?? "trial")
      }

      if (invRes.status === "fulfilled" && invRes.value?.invoices) {
        setInvoices(invRes.value.invoices)
      }

      if (usageRes.status === "fulfilled" && usageRes.value) {
        setUsage(usageRes.value)
      }

      if (analyticsRes.status === "fulfilled" && analyticsRes.value) {
        setAnalytics(analyticsRes.value)
      }
    } catch (error) {
      console.error("Failed to fetch billing data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpgrade = async (planId: PlanId) => {
    setProcessing(true)
    try {
      const data = await api.createOrder(planId, billingCycle)
      if (data.order) {
        // Open Razorpay checkout
        if (typeof window !== "undefined" && (window as any).Razorpay) {
          const options = {
            key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
            amount: data.order.amount,
            currency: data.order.currency,
            name: "SentinelX",
            description: `${PLANS[planId].name} Plan - ${billingCycle}`,
            order_id: data.order.id,
            prefill: {
              name: session?.user?.name ?? "SentinelX User",
              email: session?.user?.email ?? "user@sentinelx.dev",
            },
            theme: { color: "#0f766e" },
            handler: async (response: any) => {
              const verifyRes = await api.verifyPayment(
                response.razorpay_order_id,
                response.razorpay_payment_id,
                response.razorpay_signature
              )
              if (verifyRes.success) {
                fetchBillingData()
              }
            },
            modal: { ondismiss: () => setProcessing(false) },
          }
          const rzp = new (window as any).Razorpay(options)
          rzp.open()
        } else {
          // Demo mode
          setTimeout(() => {
            fetchBillingData()
            setProcessing(false)
          }, 1000)
        }
      }
    } catch (error) {
      console.error("Upgrade failed:", error)
      setProcessing(false)
    }
  }

  const getFeatureIcon = (enabled: boolean) => (
    enabled ? (
      <CheckCircle2 className="h-4 w-4 text-status-low" />
    ) : (
      <XCircle className="h-4 w-4 text-text-muted" />
    )
  )

  const formatPrice = (price: number) => `₹${price.toLocaleString()}`

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Billing</h1>
          <p className="mt-1 text-sm text-text-muted">
            Manage your subscription, invoices, and usage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-border-default bg-white/[0.02] p-1">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={cn(
                "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
                billingCycle === "monthly"
                  ? "bg-accent/20 text-accent-light"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle("yearly")}
              className={cn(
                "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
                billingCycle === "yearly"
                  ? "bg-accent/20 text-accent-light"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              Yearly
              <span className="ml-1.5 text-[10px] text-status-low">Save 17%</span>
            </button>
          </div>
        </div>
      </div>

      {/* Current Plan */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={cn(
              "flex h-12 w-12 items-center justify-center rounded-xl",
              currentPlan === "starter" && "bg-status-info/15",
              currentPlan === "professional" && "bg-status-high/15",
              currentPlan === "enterprise" && "bg-accent/15",
            )}>
              {currentPlan === "starter" && <Zap className="h-6 w-6 text-status-info" />}
              {currentPlan === "professional" && <ShieldCheck className="h-6 w-6 text-status-high" />}
              {currentPlan === "enterprise" && <Crown className="h-6 w-6 text-accent-light" />}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">{PLANS[currentPlan].name} Plan</h2>
              <p className="text-sm text-text-muted">
                {subscription?.status === "active" ? "Active" : "No active subscription"}
                {subscription?.current_end && ` · Renews ${new Date(subscription.current_end * 1000).toLocaleDateString()}`}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-text-primary">
              {formatPrice(billingCycle === "yearly" ? PLANS[currentPlan].yearlyPrice : PLANS[currentPlan].price)}
              <span className="text-sm font-normal text-text-muted">/month</span>
            </p>
            {billingCycle === "yearly" && (
              <p className="text-xs text-status-low">Billed yearly: {formatPrice(PLANS[currentPlan].yearlyPrice)}</p>
            )}
          </div>
        </div>
        {currentPlan !== "enterprise" && (
          <button
            onClick={() => handleUpgrade("enterprise")}
            disabled={processing}
            className="mt-4 w-full flex items-center justify-center gap-2 rounded-lg bg-accent/20 px-4 py-2 text-sm font-semibold text-accent-light transition-colors hover:bg-accent/30 disabled:opacity-60"
          >
            {processing ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
            Upgrade to Enterprise
          </button>
        )}
      </div>

      {/* Pricing Comparison */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
        <h2 className="mb-4 text-lg font-semibold text-text-primary">Compare Plans</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border-subtle">
                <th className="text-left py-3 px-4 font-medium text-text-secondary">Feature</th>
                {(["trial", "starter", "professional", "enterprise"] as PlanId[]).map((pid) => (
                  <th key={pid} className="text-center py-3 px-4 font-medium text-text-primary">
                    {PLANS[pid].name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { key: "users", label: "Users", icon: Users },
                { key: "aiRequests", label: "AI Requests/month", icon: Zap },
                { key: "storage", label: "Storage (GB)", icon: Database },
                { key: "compliancePacks", label: "Compliance Packs", icon: ShieldCheck },
                { key: "prioritySupport", label: "Priority Support", icon: FileText },
                { key: "socDashboard", label: "SOC Dashboard", icon: BarChart3 },
                { key: "unlimitedAuditLogs", label: "Unlimited Audit Logs", icon: Database },
                { key: "enterpriseSSO", label: "Enterprise SSO", icon: Building2 },
                { key: "apiAccess", label: "API Access", icon: ExternalLink },
                { key: "customPolicies", label: "Custom Policies", icon: Settings },
              ].map((feature) => (
                <tr key={feature.key} className="border-b border-border-subtle/50">
                  <td className="py-3 px-4 flex items-center gap-2 text-text-secondary">
                    <feature.icon className="h-4 w-4" />
                    {feature.label}
                  </td>
{(["starter", "professional", "enterprise"] as PlanId[]).map((pid) => {
                      const planFeatures = PLANS[pid].features
                      const value = planFeatures[feature.key as keyof typeof planFeatures]
                      return (
                      <td key={pid} className="text-center py-3 px-4">
                        {typeof value === "boolean" ? (
                          getFeatureIcon(value)
                        ) : value === -1 ? (
                          <span className="text-text-primary font-medium">Unlimited</span>
                        ) : (
                          <span className="text-text-primary font-medium">
                            {typeof value === "number" ? value.toLocaleString() : value}
                          </span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Usage Metering */}
      {usage && (
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-text-primary">
            <BarChart3 className="h-5 w-5" /> Usage Metering
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { key: "protectedPrompts", label: "Protected Prompts", current: usage.current.protectedPrompts, limit: usage.limits.protectedPrompts },
              { key: "llmCalls", label: "LLM Calls", current: usage.current.llmCalls, limit: usage.limits.llmCalls },
              { key: "storage", label: "Storage (GB)", current: usage.current.storageUsed, limit: usage.limits.storage },
              { key: "incidents", label: "Incidents", current: usage.current.incidents, limit: usage.limits.incidents },
              { key: "reportsGenerated", label: "Reports Generated", current: usage.current.reportsGenerated, limit: usage.limits.reportsGenerated },
              { key: "complianceChecks", label: "Compliance Checks", current: usage.current.complianceChecks, limit: usage.limits.complianceChecks },
            ].map((item) => (
              <div key={item.key} className="rounded-lg border border-border-default bg-white/[0.02] p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-secondary">{item.label}</span>
                  <span className="mono text-sm text-text-primary">
                    {item.current.toLocaleString()} {item.limit === -1 ? "" : `/ ${item.limit.toLocaleString()}`}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className="h-full rounded-full bg-accent transition-all duration-500"
                    style={{ width: item.limit === -1 ? "50%" : `${Math.min(100, (item.current / item.limit) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invoices */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Receipt className="h-5 w-5" /> Invoices
          </h2>
          <Badge variant="outline">{invoices.length} invoices</Badge>
        </div>
        {invoices.length === 0 ? (
          <div className="text-center py-8 text-text-muted">
            <Receipt className="mx-auto mb-2 h-8 w-8 text-text-muted/40" />
            <p>No invoices yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {invoices.map((inv: any) => (
              <div
                key={inv.id}
                className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] p-4"
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-lg",
                    inv.status === "paid" && "bg-status-low/15",
                    inv.status === "pending" && "bg-status-medium/15",
                    inv.status === "failed" && "bg-status-critical/15",
                  )}>
                    {inv.status === "paid" && <CheckCircle2 className="h-5 w-5 text-status-low" />}
                    {inv.status === "pending" && <Clock className="h-5 w-5 text-status-medium" />}
                    {inv.status === "failed" && <AlertCircle className="h-5 w-5 text-status-critical" />}
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">{inv.description ?? "Invoice"}</p>
                    <p className="text-sm text-text-muted">
                      {new Date(inv.date * 1000).toLocaleDateString()} · {inv.currency} {(inv.amount / 100).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={inv.status === "paid" ? "success" : inv.status === "pending" ? "warning" : "danger"}>
                    {inv.status}
                  </Badge>
                  <button aria-label="Download invoice" className="flex items-center justify-center rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-xs text-text-secondary hover:bg-white/[0.04]">
                    <Download className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Billing Analytics */}
      {analytics && (
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-text-primary">
            <TrendingUp className="h-5 w-5" /> Billing Analytics
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
              <p className="text-sm font-medium text-text-muted">MRR</p>
              <p className="mt-1 mono text-2xl font-bold text-text-primary">₹{(analytics.mrr / 100).toLocaleString()}</p>
            </div>
            <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
              <p className="text-sm font-medium text-text-muted">ARR</p>
              <p className="mt-1 mono text-2xl font-bold text-text-primary">₹{(analytics.arr / 100).toLocaleString()}</p>
            </div>
            <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
              <p className="text-sm font-medium text-text-muted">Active Subscriptions</p>
              <p className="mt-1 mono text-2xl font-bold text-text-primary">{analytics.activeSubscriptions}</p>
            </div>
            <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
              <p className="text-sm font-medium text-text-muted">Payment Success</p>
              <p className="mt-1 mono text-2xl font-bold text-status-low">{analytics.paymentSuccessRate}%</p>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-accent-light" />
        </div>
      )}
    </div>
  )
}