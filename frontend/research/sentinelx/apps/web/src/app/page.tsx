import Link from "next/link"
import {
  ArrowRight,
  BarChart3,
  Bot,
  Check,
  ChevronRight,
  Cpu,
  FileSearch,
  Gauge,
  KeyRound,
  Lock,
  MemoryStick,
  Radar,
  ScanSearch,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Wand2,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Architecture", href: "#architecture" },
  { label: "Enterprise", href: "#enterprise" },
  { label: "Pricing", href: "#pricing" },
  { label: "FAQ", href: "#faq" },
]

const FEATURES = [
  { icon: ScanSearch, title: "8-Agent Pipeline", desc: "Inspector, Secret Detection, Policy, Risk, Rewriter, LLM Gateway, Audit, and Memory agents inspect every request before it reaches a model." },
  { icon: ShieldAlert, title: "Secret & PII Detection", desc: "30+ deterministic pattern rules catch AWS keys, API tokens, JWTs, credit cards, PHI, and more — with zero false-positive drift." },
  { icon: Gauge, title: "Enterprise Risk Scoring", desc: "A composite risk score synthesizes data sensitivity, intent, policy exposure, and historical behavior into a 0–100 decision." },
  { icon: Wand2, title: "Intent-Preserving Rewriting", desc: "Sensitive entities are redacted before transmission while the prompt's intent is preserved — so safe requests keep working." },
  { icon: Lock, title: "Tamper-Evident Audit", desc: "Every decision is SHA-256 hashed into an immutable audit chain with full context for compliance and investigations." },
  { icon: Bot, title: "AI Copilot", desc: "Ask why a prompt was blocked, which policy triggered, or how to improve posture — answered live from the audit chain." },
  { icon: Radar, title: "Threat Intelligence", desc: "Heatmaps, attack categories, department risk, and hourly trends turn raw events into board-ready security intelligence." },
  { icon: Cpu, title: "Zero-Latency Gateway", desc: "An inline firewall sits between users and LLM providers — OpenAI, Gemini, Claude, Ollama — with sub-100ms overhead." },
]

const PIPELINE = [
  { name: "Inspector", icon: ScanSearch, desc: "Intent & sensitivity" },
  { name: "Detection", icon: KeyRound, desc: "Pattern matching" },
  { name: "Policy", icon: ShieldCheck, desc: "Regulation checks" },
  { name: "Risk", icon: Gauge, desc: "Composite scoring" },
  { name: "Rewriter", icon: Wand2, desc: "Sanitization" },
  { name: "Gateway", icon: Cpu, desc: "Model routing" },
  { name: "Audit", icon: FileSearch, desc: "Immutable log" },
  { name: "Memory", icon: MemoryStick, desc: "Behavior context" },
]

const COMPLIANCE = ["SOC 2", "GDPR", "HIPAA", "PCI DSS", "ISO 27001"]

const PLANS = [
  {
    name: "Community",
    price: "$0",
    period: "/month",
    desc: "For individuals and open-source projects",
    features: ["1 gateway", "8-agent pipeline", "Core detection rules", "7-day audit retention", "Community support"],
    cta: "Get started",
    highlighted: false,
  },
  {
    name: "Business",
    price: "$49",
    period: "/month",
    desc: "For growing teams shipping AI to production",
    features: ["Unlimited gateways", "All 30+ detection rules", "Policy center & compliance", "90-day audit retention", "AI Copilot", "Export to PDF / CSV / JSON", "Priority support"],
    cta: "Start free trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    desc: "For organizations with strict compliance needs",
    features: ["SSO & RBAC", "On-prem deployment", "Unlimited retention", "Custom policy packs", "Dedicated security engineer", "99.99% uptime SLA", "Dedicated Slack support"],
    cta: "Talk to sales",
    highlighted: false,
  },
]

const FAQS = [
  { q: "What is SentinelX?", a: "SentinelX is an enterprise AI governance firewall that sits between your users and LLM providers. Every prompt is inspected by a pipeline of 8 agents before it reaches a model, so sensitive data is detected, blocked, or sanitized in real time." },
  { q: "How does it detect secrets and PII?", a: "A dedicated secret-detection agent runs 30+ deterministic pattern rules — AWS keys, Google API keys, JWTs, MongoDB URIs, credit cards, emails, phone numbers, patient identifiers, and more — with per-rule confidence scoring and redaction support." },
  { q: "Does SentinelX require an external LLM to work?", a: "No. Every decision is made by deterministic rules and a rule-based copilot that reads your live audit chain. This keeps decisions fast, explainable, and auditable." },
  { q: "Which providers are supported?", a: "OpenAI, Google Gemini, Anthropic Claude, OpenRouter, and local models via Ollama. The adapter architecture makes it trivial to add more." },
  { q: "Is the audit log tamper-evident?", a: "Yes. Every record is hashed and chained, giving you a verifiable, immutable trail for compliance reviews and incident investigations." },
  { q: "How fast is the gateway?", a: "Typical pipeline overhead is under 100ms. Detection and policy agents run in parallel and the risk engine scores instantly from cached features." },
]

function PricingToggle() {
  return (
    <div className="flex items-center gap-2 text-xs text-text-muted">
      <span>Monthly</span>
      <span className="h-5 w-9 rounded-full border border-accent/40 bg-accent/20 p-0.5">
        <span className="ml-4 block h-4 w-4 rounded-full bg-accent-light" />
      </span>
      <span>Annual <span className="text-status-low">-20%</span></span>
    </div>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Nav */}
      <header className="fixed top-0 z-50 flex h-16 w-full items-center justify-between border-b border-border-subtle bg-bg-primary/80 px-6 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent shadow-glow">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold tracking-tight text-text-primary">
              Sentinel<span className="text-accent-light">X</span>
            </span>
            <span className="text-[10px] uppercase tracking-widest text-text-muted">AI Governance Firewall</span>
          </div>
        </div>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="rounded-lg px-3 py-2 text-sm text-text-secondary transition-colors hover:text-text-primary">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link href="/dashboard" className="tech-chip hidden hover:border-accent sm:flex">
            Live demo
          </Link>
          <Link href="/dashboard" className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white shadow-glow transition-all hover:bg-accent-light">
            Open console
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-32">
        <div className="pointer-events-none absolute inset-0 grid-bg opacity-40" />
        <div className="pointer-events-none absolute -top-40 left-1/2 h-96 w-[700px] -translate-x-1/2 rounded-full bg-accent/10 blur-3xl" />

        <div className="relative mx-auto max-w-5xl text-center">
            <div className="mx-auto mb-6 flex w-fit items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs text-accent-light">
              <Sparkles className="h-3.5 w-3.5" />
              Enterprise AI Security · Built for the AI Frontier Challenge
            </div>

            <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight text-text-primary sm:text-6xl">
              Stop every sensitive prompt{" "}
              <span className="text-gradient-teal">before it reaches the model</span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-balance text-base leading-relaxed text-text-secondary sm:text-lg">
              SentinelX inspects every LLM request through an 8-agent pipeline — detecting secrets, enforcing policy, scoring risk, and rewriting sensitive content in real time. With a tamper-evident audit trail, security intelligence, and an AI copilot.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link href="/dashboard" className="group flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white shadow-glow transition-all hover:bg-accent-light">
                Launch live console
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <a href="#features" className="flex items-center gap-2 rounded-xl border border-border-strong px-6 py-3 text-sm font-semibold text-text-secondary transition-colors hover:border-accent/50 hover:text-text-primary">
                Explore features
              </a>
            </div>

            <div className="mt-10 flex flex-wrap items-center justify-center gap-4 text-xs text-text-muted">
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-status-low" /> No external LLM required</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-status-low" /> Real-time inline interception</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-status-low" /> Tamper-evident audit</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-status-low" /> SOC 2 · GDPR · HIPAA · PCI DSS</span>
            </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl scroll-mt-24 px-6 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">A full governance pipeline, out of the box</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-text-secondary">
            Eight specialized agents work in sequence — and often in parallel — to classify, detect, enforce, score, rewrite, route, and audit every request.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="glass-card card-glow group p-5">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15 transition-all group-hover:bg-accent/25 group-hover:shadow-glow">
                <f.icon className="h-5 w-5 text-accent-light" />
              </div>
              <h3 className="text-sm font-semibold text-text-primary">{f.title}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-text-muted">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="mx-auto max-w-6xl scroll-mt-24 px-6 py-20">
        <div className="glass-card relative overflow-hidden p-8">
          <div className="pointer-events-none absolute inset-0 grid-bg opacity-30" />
          <div className="relative">
            <div className="mb-8 text-center">
              <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">The 8-agent pipeline</h2>
              <p className="mx-auto mt-3 max-w-xl text-sm text-text-secondary">
                Every prompt flows through the same deterministic, explainable chain — with streaming updates to the live console.
              </p>
            </div>

            <div className="flex flex-col gap-0 lg:flex-row lg:items-stretch lg:gap-2">
              {PIPELINE.map((p, i) => (
                <div key={p.name} className="relative flex-1">
                  <div className={cn("h-full rounded-xl border p-4 text-center", i % 2 === 0 ? "border-accent/30 bg-accent/10" : "border-border-default bg-white/[0.02]")}>
                    <p.icon className={cn("mx-auto h-5 w-5", i % 2 === 0 ? "text-accent-light" : "text-text-muted")} />
                    <p className="mt-2 text-xs font-semibold text-text-primary">{p.name}</p>
                    <p className="mt-0.5 text-[10px] text-text-muted">{p.desc}</p>
                  </div>
                  {i < PIPELINE.length - 1 && (
                    <div className="absolute -right-2 top-1/2 z-10 hidden -translate-y-1/2 lg:block">
                      <ChevronRight className="h-4 w-4 text-accent-light" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
              {COMPLIANCE.map((c) => (
                <span key={c} className="tech-chip">{c}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Enterprise benefits */}
      <section id="enterprise" className="mx-auto max-w-6xl scroll-mt-24 px-6 py-20">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">Built for the SOC, the CISO, and the auditor</h2>
            <p className="mt-4 text-sm leading-relaxed text-text-secondary">
              SentinelX isn&apos;t just a scanner — it&apos;s a complete security posture platform. Executives get a global security score. Analysts get incident investigation. Auditors get an immutable chain. Users get their job done without leaking data.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                { icon: Gauge, text: "Executive Security Center with a global security score, org risk index, and compliance health." },
                { icon: Bot, text: "AI Copilot that answers 'why was this blocked?' directly from the audit chain." },
                { icon: FileSearch, text: "Incident Investigation with risk reasoning, matched patterns, and recommended actions." },
                { icon: BarChart3, text: "Security Intelligence with threat heatmaps, attack categories, and department risk." },
              ].map((b) => (
                <li key={b.text} className="flex items-start gap-3">
                  <span className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-accent/15">
                    <b.icon className="h-4 w-4 text-accent-light" />
                  </span>
                  <span className="text-sm text-text-secondary">{b.text}</span>
                </li>
              ))}
            </ul>
            <Link href="/dashboard" className="group mt-8 inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-glow transition-all hover:bg-accent-light">
              See it live
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>

          <div className="relative">
            <div className="glass-card card-glow p-6">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-status-low" />
                  <span className="text-xs font-semibold text-text-primary">Enterprise Security Posture</span>
                </div>
                <span className="flex items-center gap-1.5 text-[10px] text-status-low"><span className="h-1.5 w-1.5 rounded-full bg-status-low pulse-dot" /> LIVE</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Global Security Score", value: "94/100", tone: "text-status-low" },
                  { label: "Active Incidents", value: "3", tone: "text-status-medium" },
                  { label: "Detection Accuracy", value: "99.2%", tone: "text-status-low" },
                  { label: "Compliance Health", value: "98%", tone: "text-accent-light" },
                ].map((s) => (
                  <div key={s.label} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                    <p className="text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
                    <p className={cn("mono mt-1 text-xl font-semibold", s.tone)}>{s.value}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2 text-xs">
                  <span className="text-text-secondary">Top violated policy</span>
                  <span className="text-status-high">PII Handling · 12</span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2 text-xs">
                  <span className="text-text-secondary">Dept. at highest risk</span>
                  <span className="text-status-medium">HR · 34%</span>
                </div>
              </div>
            </div>
            <div className="pointer-events-none absolute -right-4 -top-4 h-24 w-24 rounded-full bg-accent/20 blur-2xl" />
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-6xl scroll-mt-24 px-6 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">Simple, transparent pricing</h2>
          <div className="mt-4 flex justify-center"><PricingToggle /></div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {PLANS.map((p) => (
            <div
              key={p.name}
              className={cn(
                "glass-card relative flex flex-col p-6",
                p.highlighted && "glass-card-accent border-accent/50",
              )}
            >
              {p.highlighted && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-accent px-3 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-white shadow-glow">
                  Most popular
                </span>
              )}
              <h3 className="text-sm font-semibold text-text-primary">{p.name}</h3>
              <p className="mt-1 text-xs text-text-muted">{p.desc}</p>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="mono text-3xl font-bold text-text-primary">{p.price}</span>
                <span className="text-xs text-text-muted">{p.period}</span>
              </div>
              <ul className="mt-6 flex-1 space-y-2.5">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-xs text-text-secondary">
                    <Check className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-accent-light" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/dashboard"
                className={cn(
                  "mt-8 flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold transition-all",
                  p.highlighted
                    ? "bg-accent text-white shadow-glow hover:bg-accent-light"
                    : "border border-border-strong text-text-secondary hover:border-accent/50 hover:text-text-primary",
                )}
              >
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl scroll-mt-24 px-6 py-20">
        <div className="mb-10 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">Frequently asked questions</h2>
        </div>
        <div className="space-y-3">
          {FAQS.map((f) => (
            <details key={f.q} className="glass-card group p-5">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-medium text-text-primary">
                {f.q}
                <ChevronRight className="h-4 w-4 flex-shrink-0 text-text-muted transition-transform group-open:rotate-90" />
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-text-secondary">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 pb-24">
        <div className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl border border-accent/30 bg-accent/10 p-12 text-center">
          <div className="pointer-events-none absolute inset-0 grid-bg opacity-30" />
          <div className="pointer-events-none absolute -top-20 left-1/2 h-64 w-96 -translate-x-1/2 rounded-full bg-accent/20 blur-3xl" />
          <div className="relative">
            <h2 className="text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">Ready to secure your AI?</h2>
            <p className="mx-auto mt-3 max-w-lg text-sm text-text-secondary">
              Run the full live demo — watch SentinelX intercept AWS secrets, credit cards, patient data, and API keys in real time.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link href="/dashboard" className="group flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white shadow-glow transition-all hover:bg-accent-light">
                Launch live console
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <Link href="/demo" className="flex items-center gap-2 rounded-xl border border-border-strong px-6 py-3 text-sm font-semibold text-text-secondary transition-colors hover:border-accent/50 hover:text-text-primary">
                <Zap className="h-4 w-4 text-accent-light" /> Presentation mode
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border-subtle px-6 py-12">
        <div className="mx-auto grid max-w-6xl gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent shadow-glow">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div className="flex flex-col leading-tight">
                <span className="text-sm font-semibold tracking-tight text-text-primary">
                  Sentinel<span className="text-accent-light">X</span>
                </span>
                <span className="text-[10px] uppercase tracking-widest text-text-muted">AI Governance Firewall</span>
              </div>
            </div>
            <p className="mt-4 max-w-sm text-xs leading-relaxed text-text-muted">
              Enterprise AI security that detects, prevents, explains, and audits sensitive data leakage to large language models — in real time.
            </p>
          </div>

          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">Product</p>
            <ul className="space-y-2 text-xs text-text-secondary">
              <li><Link href="/dashboard" className="hover:text-accent-light">Console</Link></li>
              <li><Link href="/scanner" className="hover:text-accent-light">Scanner</Link></li>
              <li><Link href="/intelligence" className="hover:text-accent-light">Intelligence</Link></li>
              <li><Link href="/copilot" className="hover:text-accent-light">Copilot</Link></li>
              <li><Link href="/demo" className="hover:text-accent-light">Demo Mode</Link></li>
            </ul>
          </div>

          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">Compliance</p>
            <ul className="space-y-2 text-xs text-text-secondary">
              <li>SOC 2 Type II</li>
              <li>GDPR</li>
              <li>HIPAA</li>
              <li>PCI DSS</li>
              <li>ISO 27001</li>
            </ul>
          </div>
        </div>

        <div className="mx-auto mt-12 flex max-w-6xl flex-wrap items-center justify-between gap-4 border-t border-border-subtle pt-6">
          <p className="text-[11px] text-text-muted">© {new Date().getFullYear()} SentinelX. Built for the AI Frontier Challenge.</p>
          <div className="flex items-center gap-4 text-[11px] text-text-muted">
            <span className="flex items-center gap-1.5"><Lock className="h-3 w-3" /> Audit chain active</span>
            <span className="flex items-center gap-1.5"><ShieldCheck className="h-3 w-3 text-status-low" /> All systems operational</span>
          </div>
        </div>
      </footer>
    </div>
  )
}