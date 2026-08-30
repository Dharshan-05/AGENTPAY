"use client"

import { useState } from "react"
import {
  Zap,
  ShieldCheck,
  Database,
  Crown,
  Users,
  FileText,
  Building2,
  ExternalLink,
  Settings,
  CheckCircle2,
  ArrowRight,
  Loader2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"

const PLANS = {
  trial: {
    id: "trial",
    name: "Trial",
    price: 9,
    yearlyPrice: 9,
    currency: "INR",
    interval: "one_time",
    description: "Perfect for trying SentinelX with full features for a limited time",
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
    cta: "Start Trial",
    popular: false,
  },
  starter: {
    id: "starter",
    name: "Starter",
    price: 49,
    yearlyPrice: 490,
    currency: "INR",
    interval: "monthly",
    description: "Perfect for small teams getting started with AI governance",
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
    cta: "Start Free Trial",
    popular: false,
  },
  professional: {
    id: "professional",
    name: "Professional",
    price: 149,
    yearlyPrice: 1490,
    currency: "INR",
    interval: "monthly",
    description: "For growing companies needing advanced security features",
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
    cta: "Start Free Trial",
    popular: true,
  },
  enterprise: {
    id: "enterprise",
    name: "Enterprise",
    price: 499,
    yearlyPrice: 4990,
    currency: "INR",
    interval: "monthly",
    description: "Complete AI governance for large organizations",
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
    cta: "Contact Sales",
    popular: false,
  },
} as const

type PlanId = keyof typeof PLANS

export default function PricingClient() {
  const { user } = useAuth()
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly")
  const [selectedPlan, setSelectedPlan] = useState<PlanId | null>(null)
  const [processing, setProcessing] = useState(false)

  const handleSelect = async (planId: PlanId) => {
    setSelectedPlan(planId)
    if (planId === "enterprise") {
      // Redirect to contact sales or demo
      window.location.href = "/demo"
      return
    }
    setProcessing(true)
    try {
      const plan = PLANS[planId]
      const cycle = plan.interval === "one_time" ? "one_time" : billingCycle
      const data = await api.createOrder(planId, cycle)
      if (data.order && typeof window !== "undefined" && (window as any).Razorpay) {
        const options = {
          key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
          amount: data.amount ?? data.order.amount,
          currency: data.order.currency,
          name: "SentinelX",
          description: `${PLANS[planId].name} Plan - ${cycle}`,
          order_id: data.order.id,
          prefill: {
            name: user?.name ?? "SentinelX User",
            email: user?.email ?? "user@sentinelx.dev",
          },
          theme: { color: "#0f766e" },
          handler: async (response: any) => {
            const verifyRes = await api.verifyPayment(
              response.razorpay_order_id,
              response.razorpay_payment_id,
              response.razorpay_signature
            )
            if (verifyRes.success) {
              window.location.href = "/billing"
            }
          },
          modal: { ondismiss: () => setProcessing(false) },
        }
        const rzp = new (window as any).Razorpay(options)
        rzp.open()
      } else {
        // Demo mode
        setTimeout(() => {
          window.location.href = "/billing"
          setProcessing(false)
        }, 1000)
      }
    } catch (error) {
      console.error("Purchase failed:", error)
      setProcessing(false)
    }
  }

  const getFeatureIcon = (enabled: boolean) => (
    enabled ? (
      <CheckCircle2 className="h-4 w-4 text-status-low" />
    ) : (
      <span className="h-4 w-4 text-text-muted/30">—</span>
    )
  )

  return (
    <div className="min-h-screen bg-bg-page">
      {/* Hero */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-4 flex items-center justify-center gap-2">
              <span className="rounded-full bg-accent/15 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-accent-light">
                Transparent Pricing
              </span>
            </div>
            <h1 className="mb-6 text-4xl font-bold tracking-tight text-text-primary sm:text-5xl lg:text-6xl">
              Simple, predictable pricing for every team
            </h1>
            <p className="mb-8 text-lg text-text-muted max-w-2xl mx-auto">
              No hidden fees. No per-seat surprises. All plans include our full AI governance engine,
              real-time threat detection, and compliance automation.
            </p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => setBillingCycle("monthly")}
                className={cn(
                  "px-4 py-2.5 text-sm font-medium rounded-lg transition-colors",
                  billingCycle === "monthly"
                    ? "bg-accent/20 text-accent-light"
                    : "bg-white/[0.03] text-text-secondary hover:bg-white/[0.05]"
                )}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle("yearly")}
                className={cn(
                  "flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors",
                  billingCycle === "yearly"
                    ? "bg-accent/20 text-accent-light"
                    : "bg-white/[0.03] text-text-secondary hover:bg-white/[0.05]"
                )}
              >
                Yearly
                <span className="ml-2 rounded-full bg-status-low/15 px-2 py-0.5 text-[10px] font-semibold text-status-low">
                  Save 17%
                </span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Plans Grid */}
      <section className="py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-3">
            {(["trial", "starter", "professional", "enterprise"] as PlanId[]).map((pid) => {
              const plan = PLANS[pid]
              const isOneTime = plan.interval === "one_time"
              return (
                <article
                  key={pid}
                  className={cn(
                    "relative rounded-2xl border p-8 transition-all duration-200",
                    plan.popular
                      ? "border-accent/40 bg-accent/[0.03] shadow-[0_0_0_1px_theme(colors.accent)]"
                      : "border-border-default bg-white/[0.02] hover:border-border-strong",
                  )}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="rounded-full bg-accent px-3 py-1 text-xs font-semibold uppercase tracking-wider text-bg-primary">
                        Most Popular
                      </span>
                    </div>
                  )}

                  <div className="mb-6">
                    <div className={cn(
                      "flex h-14 w-14 items-center justify-center rounded-xl mx-auto mb-4",
                      pid === "trial" && "bg-status-low/15",
                      pid === "starter" && "bg-status-info/15",
                      pid === "professional" && "bg-status-high/15",
                      pid === "enterprise" && "bg-accent/15",
                    )}>
                      {pid === "trial" && <Zap className="h-7 w-7 text-status-low" />}
                      {pid === "starter" && <Zap className="h-7 w-7 text-status-info" />}
                      {pid === "professional" && <ShieldCheck className="h-7 w-7 text-status-high" />}
                      {pid === "enterprise" && <Crown className="h-7 w-7 text-accent-light" />}
                    </div>
                    <h3 className="mb-2 text-center text-2xl font-bold text-text-primary">{plan.name}</h3>
                    <p className="text-center text-text-muted">{plan.description}</p>
                  </div>

                  <div className="mb-6 text-center">
                    <div className="mb-2">
                      <span className="text-4xl font-bold text-text-primary">
                        {isOneTime
                          ? `₹${plan.price.toLocaleString()}`
                          : billingCycle === "yearly"
                          ? `₹${plan.yearlyPrice.toLocaleString()}`
                          : `₹${plan.price.toLocaleString()}`}
                      </span>
                      {isOneTime ? (
                        <span className="text-text-muted"> (one-time)</span>
                      ) : (
                        <span className="text-text-muted">/month</span>
                      )}
                    </div>
                    {!isOneTime && billingCycle === "yearly" && (
                      <p className="text-sm text-status-low">
                        Billed yearly: ₹{plan.yearlyPrice.toLocaleString()}
                      </p>
                    )}
                    {!isOneTime && billingCycle === "monthly" && (
                      <p className="text-sm text-text-muted">
                        Or ₹{plan.yearlyPrice.toLocaleString()}/year (save 17%)
                      </p>
                    )}
                    {isOneTime && (
                      <p className="text-sm text-status-low">One-time payment</p>
                    )}
                  </div>

                  <ul className="mb-8 space-y-3">
                    {[
                      { key: "users", label: "Users", value: plan.features.users, icon: Users },
                      { key: "aiRequests", label: "AI Requests/month", value: plan.features.aiRequests, icon: Zap },
                      { key: "storage", label: "Storage (GB)", value: plan.features.storage, icon: Database },
                      { key: "compliancePacks", label: "Compliance Packs", value: plan.features.compliancePacks, icon: ShieldCheck },
                      { key: "prioritySupport", label: "Priority Support", value: plan.features.prioritySupport, icon: FileText },
                      { key: "socDashboard", label: "SOC Dashboard", value: plan.features.socDashboard, icon: Building2 },
                      { key: "unlimitedAuditLogs", label: "Unlimited Audit Logs", value: plan.features.unlimitedAuditLogs, icon: Database },
                      { key: "enterpriseSSO", label: "Enterprise SSO (SAML/OIDC)", value: plan.features.enterpriseSSO, icon: Building2 },
                      { key: "apiAccess", label: "API Access", value: plan.features.apiAccess, icon: ExternalLink },
                      { key: "customPolicies", label: "Custom Policies", value: plan.features.customPolicies, icon: Settings },
                    ].map((feature) => (
                      <li key={feature.key} className="flex items-center gap-3 text-sm">
                        {getFeatureIcon(typeof feature.value === "boolean" ? feature.value : feature.value > 0)}
                        <span className={cn(
                          typeof feature.value === "boolean"
                            ? feature.value ? "text-text-primary" : "text-text-muted"
                            : "text-text-primary",
                        )}>
                          {feature.label}
                          {typeof feature.value === "number" && feature.value > 0 && (
                            <span className="ml-1 text-text-muted">({feature.value === -1 ? "Unlimited" : feature.value.toLocaleString()})</span>
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => handleSelect(pid)}
                    disabled={processing}
                    className={cn(
                      "w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200",
                      plan.popular
                        ? "bg-accent text-bg-primary hover:bg-accent-light/90"
                        : "bg-white/[0.03] text-text-primary border border-border-default hover:bg-white/[0.05]",
                      processing && "opacity-60 cursor-not-allowed",
                    )}
                  >
                    {processing && selectedPlan === pid ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Processing...
                      </span>
                    ) : (
                      plan.cta
                    )}
                  </button>
                </article>
              )
            })}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 lg:py-24 bg-white/[0.01]">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="mb-12 text-3xl font-bold tracking-tight text-text-primary">Frequently Asked Questions</h2>
          <div className="space-y-4 text-left">
            {[
              {
                q: "Can I switch plans later?",
                a: "Yes, you can upgrade or downgrade at any time. Changes take effect immediately, and we'll prorate the difference."
              },
              {
                q: "What payment methods do you accept?",
                a: "We accept all major credit cards, UPI, net banking, and wallets via Razorpay. Enterprise customers can also pay via invoice."
              },
              {
                q: "Is there a free trial?",
                a: "Yes, Starter and Professional plans include a 14-day free trial with full feature access. No credit card required to start."
              },
              {
                q: "What happens after the trial ends?",
                a: "You'll be prompted to choose a plan. If you don't upgrade, your account will be paused but all data is preserved for 30 days."
              },
              {
                q: "Do you offer discounts for non-profits or educational institutions?",
                a: "Yes! We offer 50% off for qualified non-profits and educational institutions. Contact our sales team to learn more."
              },
              {
                q: "How does usage-based billing work?",
                a: "All plans include generous usage limits. Enterprise plans have unlimited usage. We'll notify you at 80% and 95% of your limits."
              },
            ].map((faq, i) => (
              <details
                key={i}
                className="group rounded-xl border border-border-default bg-white/[0.02] p-5 transition-colors hover:border-border-strong"
              >
                <summary className="flex items-center justify-between cursor-pointer font-medium text-text-primary">
                  {faq.q}
                  <ArrowRight className={cn("h-5 w-5 text-text-muted transition-transform", "group-open:rotate-90")} />
                </summary>
                <p className="mt-4 text-text-secondary">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-24">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <div className="rounded-2xl border border-accent/30 bg-accent/[0.05] p-8 lg:p-12">
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-text-primary">Ready to secure your AI workflows?</h2>
            <p className="mb-8 text-lg text-text-muted max-w-xl mx-auto">
              Join 500+ organizations protecting their data with SentinelX. Start your free trial today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={() => handleSelect("professional")}
                className="flex items-center justify-center gap-2 rounded-xl bg-accent px-8 py-3.5 text-base font-semibold text-bg-primary hover:bg-accent-light transition-colors"
              >
                <ArrowRight className="h-4 w-4" />
                Start Free Trial
              </button>
              <button className="flex items-center justify-center gap-2 rounded-xl border border-border-default bg-white/[0.03] px-8 py-3.5 text-base font-semibold text-text-primary hover:bg-white/[0.05] transition-colors">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}