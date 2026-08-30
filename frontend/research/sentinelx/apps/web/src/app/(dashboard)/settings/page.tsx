"use client"

import { useEffect, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import {
  Bell,
  Bot,
  Copy,
  Cpu,
  Globe,
  KeyRound,
  Lightbulb,
  Plus,
  RefreshCw,
  Save,
  ScrollText,
  Shield,
  SlidersHorizontal,
  Sparkles,
  ToggleRight,
  Trash2,
  Users,
  FileDown,
} from "lucide-react"
import { api, PROVIDERS, timeAgo } from "@/lib/api"
import type { PolicyRecommendation } from "@/types"
import { Badge, PageHeader, SectionTitle } from "@/components/ui/primitives"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"

function Slider({
  label,
  desc,
  value,
  max = 100,
  onChange,
}: {
  label: string
  desc: string
  value: number
  max?: number
  onChange: (v: number) => void
}) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-text-primary">{label}</p>
          <p className="text-[10px] text-text-muted">{desc}</p>
        </div>
        <span className="mono rounded-md bg-accent/10 px-2 py-0.5 text-xs font-semibold text-accent-light">{value}</span>
      </div>
      <input
        type="range"
        min={0}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label={label}
        className="mt-2 w-full cursor-pointer accent-[#0b827a]"
      />
    </div>
  )
}

function Toggle({ on, onChange, label }: { on: boolean; onChange: () => void; label?: string }) {
  return (
    <button onClick={onChange} aria-label={label ?? "Toggle"} aria-pressed={on} className="flex items-center">
      <ToggleRight className={cn("h-6 w-6 transition-colors", on ? "text-accent-light" : "text-text-muted")} />
    </button>
  )
}

interface PolicyDraft {
  name: string
  description: string
  regulation: string
  category: string
  severity: string
}

interface Token {
  id: string
  label: string
  prefix: string
  scope: string
  created: string
  lastUsed: string
}

const REGULATIONS = ["GDPR", "HIPAA", "PCI DSS", "SOC 2", "ISO 27001", "Custom"]
const CATEGORIES = ["PII", "Credentials", "Financial", "Health", "Code", "Infrastructure"]

const ROLE_DEFS = [
  { role: "Admin", color: "text-status-critical", perms: ["View audit", "Manage policies", "Manage users", "Configure gateway", "Export reports"] },
  { role: "Analyst", color: "text-accent-light", perms: ["View audit", "Triage incidents", "View policies", "Generate reports"] },
  { role: "Viewer", color: "text-text-muted", perms: ["View dashboard", "View reports"] },
]

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({})
  const [saved, setSaved] = useState(false)
  const [tab, setTab] = useState<"overview" | "policies" | "notifications" | "tokens" | "branding" | "export" | "roles">("overview")

  const [policy, setPolicy] = useState<PolicyDraft>({
    name: "",
    description: "",
    regulation: "GDPR",
    category: "PII",
    severity: "HIGH",
  })
  const [customPolicies, setCustomPolicies] = useState<Array<PolicyDraft & { id: string }>>([])
  const [aiRecs, setAiRecs] = useState<{ items: PolicyRecommendation[]; model: string | null; simulated: boolean } | null>(null)
  const [aiRecsLoading, setAiRecsLoading] = useState(false)
  const [llmStatus, setLlmStatus] = useState<{ configured: string[] } | null>(null)
  const [notifications, setNotifications] = useState({
    slack: true,
    teams: false,
    email: true,
    webhook: false,
    webhookUrl: "https://hooks.example.com/sentinelx",
  })
  const [tokens, setTokens] = useState<Token[]>([])
  const [tokensLoading, setTokensLoading] = useState(false)
  const [newSecretOnce, setNewSecretOnce] = useState<{ id: string; secret: string; name: string } | null>(null)
  const [rolePerms, setRolePerms] = useState<Record<string, Record<string, boolean>>>({
    Admin: { "View audit": true, "Manage policies": true, "Manage users": true, "Configure gateway": true, "Export reports": true },
    Analyst: { "View audit": true, "Triage incidents": true, "View policies": true, "Generate reports": true },
    Viewer: { "View dashboard": true, "View reports": true },
  })
  const [branding, setBranding] = useState({
    orgName: "Acme Corporation",
    accent: "#0b827a",
    theme: "dark",
    supportEmail: "security@acme-corp.com",
    footerNote: "Confidential — internal use only",
  })
  const [exportPrefs, setExportPrefs] = useState({
    pdf: true,
    csv: true,
    json: false,
    png: true,
    schedule: "weekly",
    includePromptText: true,
    includeUserPii: false,
  })
  const toast = useToast().toast

  useEffect(() => {
    api.settings().then(setSettings).catch(() => undefined)
    api.llmStatus().then((s) => setLlmStatus({ configured: s.providers.filter((p) => p.configured).map((p) => p.id) })).catch(() => undefined)
  }, [])

  const loadTokens = () => {
    setTokensLoading(true)
    api.listMyApiKeys()
      .then((keys) => setTokens(keys.map((k: any) => ({
        id: k.id,
        label: k.name,
        prefix: k.keyPrefix,
        scope: k.scopes ? JSON.stringify(k.scopes) : "full access",
        created: k.createdAt ? new Date(k.createdAt).toLocaleDateString([], { month: "short", year: "numeric" }) : "—",
        lastUsed: k.lastUsedAt ? timeAgo(k.lastUsedAt) : "never",
      }))))
      .catch(() => undefined)
      .finally(() => setTokensLoading(false))
  }

  useEffect(() => { if (tab === "tokens") loadTokens() }, [tab])

  const save = () => {
    setSaved(true)
    toast({ kind: "success", title: "Settings saved", desc: "Gateway configuration persisted to the control plane." })
    setTimeout(() => setSaved(false), 2000)
  }

  const toggle = (key: string) => {
    setSettings((s) => ({ ...s, [key]: s[key] === "true" ? "false" : "true" }))
  }

  const num = (key: string, fallback: number) => Number(settings[key] ?? fallback)

  const createPolicy = () => {
    if (!policy.name.trim()) {
      toast({ kind: "warning", title: "Policy name required", desc: "Give the policy a name before publishing." })
      return
    }
    setCustomPolicies((p) => [...p, { ...policy, id: `pol-${Date.now()}` }])
    toast({ kind: "success", title: "Policy published", desc: `"${policy.name}" is now enforced by the Policy Engine.` })
    setPolicy({ name: "", description: "", regulation: "GDPR", category: "PII", severity: "HIGH" })
  }

  const deletePolicy = (id: string) => {
    setCustomPolicies((p) => p.filter((x) => x.id !== id))
    toast({ kind: "warning", title: "Policy removed", desc: "The custom policy was deactivated across all environments." })
  }

  const testWebhook = () => {
    toast({ kind: "live", title: "Test notification sent", desc: `Delivery attempt to ${notifications.webhookUrl}` })
  }

  const createToken = async () => {
    const name = prompt("Name for this API key:") || "New integration"
    try {
      const res = await api.createApiKey(name)
      setNewSecretOnce({ id: res.apiKey.id, secret: res.apiKey.secret, name: res.apiKey.name })
      loadTokens()
      toast({ kind: "success", title: "API key created", desc: "Copy the key now — it will only be shown once." })
    } catch {
      toast({ kind: "warning", title: "Failed to create key", desc: "Could not create API key. Please try again." })
    }
  }

  const revokeToken = async (id: string) => {
    try {
      await api.revokeApiKey(id)
      loadTokens()
      toast({ kind: "warning", title: "Token revoked", desc: "The token can no longer authenticate to the gateway." })
    } catch {
      toast({ kind: "warning", title: "Failed to revoke", desc: "Could not revoke the key. Please try again." })
    }
  }

  const TABS: Array<{ id: typeof tab; label: string; icon: typeof Shield }> = [
    { id: "overview", label: "Overview", icon: SlidersHorizontal },
    { id: "policies", label: "Policy Builder", icon: ScrollText },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "tokens", label: "API Tokens", icon: KeyRound },
    { id: "branding", label: "Branding", icon: Sparkles },
    { id: "export", label: "Export", icon: FileDown },
    { id: "roles", label: "Roles", icon: Users },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Settings"
        description="Gateway configuration, policy builder, notification rules, API tokens, and role-based access for the SentinelX deployment."
        actions={
          <button
            onClick={save}
            className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-white shadow-glow transition-colors hover:bg-accent-light"
          >
            <Save className="h-3.5 w-3.5" /> {saved ? "Saved ✓" : "Save changes"}
          </button>
        }
      />

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "flex items-center gap-1.5 rounded-lg border px-3.5 py-2 text-xs font-medium transition-all",
              tab === t.id ? "border-accent/50 bg-accent/10 text-accent-light shadow-glow" : "border-border-default bg-white/[0.02] text-text-secondary hover:border-border-strong",
            )}
          >
            <t.icon className="h-3.5 w-3.5" /> {t.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {tab === "overview" && (
          <motion.div key="overview" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <SectionTitle title="Risk Engine" sub="scoring thresholds" />
              <div className="space-y-5">
                <Slider label="Critical threshold" desc="Score above this = BLOCK with incident" value={num("risk_threshold_critical", 80)} onChange={(v) => setSettings((s) => ({ ...s, risk_threshold_critical: String(v) }))} />
                <Slider label="High threshold" desc="Score above this = BLOCK or rewrite" value={num("risk_threshold_high", 50)} onChange={(v) => setSettings((s) => ({ ...s, risk_threshold_high: String(v) }))} />
                <div className="h-px bg-border-subtle" />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Rewrite before transmit</p>
                    <p className="text-[10px] text-text-muted">Sanitize medium-risk prompts automatically</p>
                  </div>
                  <Toggle on={settings.rewrite_enabled !== "false"} onChange={() => toggle("rewrite_enabled")} label="Rewrite before transmit" />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Block on critical</p>
                    <p className="text-[10px] text-text-muted">Hard-block any critical-severity secret</p>
                  </div>
                  <Toggle on={settings.block_on_critical !== "false"} onChange={() => toggle("block_on_critical")} label="Block on critical" />
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
              <SectionTitle title="LLM Gateway" sub="provider routing" right={<Badge variant={llmStatus?.configured.length ? "success" : "info"}>{llmStatus?.configured.length ? `${llmStatus.configured.length} configured` : "simulation mode"}</Badge>} />
              <div className="space-y-2">
                {PROVIDERS.map((p) => {
                  const selected = (settings.default_provider ?? "openai") === p.id
                  const configured = llmStatus?.configured.includes(p.id)
                  return (
                    <button key={p.id} onClick={() => setSettings((s) => ({ ...s, default_provider: p.id }))} className={cn("flex w-full items-center justify-between rounded-lg border px-3 py-2.5 text-left transition-all", selected ? "border-accent/50 bg-accent/5 shadow-glow" : "border-border-default bg-white/[0.02] hover:border-border-strong")}>
                      <div className="flex items-center gap-2">
                        <Globe className={cn("h-3.5 w-3.5", selected ? "text-accent-light" : "text-text-muted")} />
                        <span className={cn("text-xs", selected ? "text-text-primary" : "text-text-secondary")}>{p.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="mono text-[10px] text-text-muted">{p.model}</span>
                        {configured ? (
                          <span className="rounded bg-low px-1.5 py-0.5 text-[9px] font-semibold uppercase text-status-low">live</span>
                        ) : (
                          <span className="rounded bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-text-muted">no key</span>
                        )}
                        {selected && (
                          <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="rounded bg-accent px-1.5 py-0.5 text-[9px] font-semibold uppercase text-white">
                            default
                          </motion.span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
              <p className="mt-3 text-[10px] leading-relaxed text-text-muted">
                Set the matching env var (OPENAI_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY) in apps/api/.env to go live. Without a key, the gateway runs in deterministic simulation mode.
              </p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="glass-card p-5">
              <SectionTitle title="Security & Audit" sub="governance controls" />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Audit retention</p>
                    <p className="text-[10px] text-text-muted">Immutable record retention period</p>
                  </div>
                  <select value={settings.retention_days ?? "365"} onChange={(e) => setSettings((s) => ({ ...s, retention_days: e.target.value }))} className="rounded-lg border border-border-default bg-bg-tertiary px-3 py-1.5 text-xs text-text-primary outline-none focus:border-accent">
                    <option value="90">90 days</option>
                    <option value="365">365 days</option>
                    <option value="730">2 years</option>
                    <option value="3650">10 years</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Alert notifications</p>
                    <p className="text-[10px] text-text-muted">Security team alerting on critical events</p>
                  </div>
                  <Toggle on onChange={() => toast({ kind: "info", title: "Alerting enabled", desc: "Critical events route to the on-call channel." })} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Session monitoring</p>
                    <p className="text-[10px] text-text-muted">Track active user sessions</p>
                  </div>
                  <Toggle on onChange={() => toast({ kind: "info", title: "Session monitoring on", desc: "Active sessions are being tracked." })} />
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }} className="glass-card p-5">
              <SectionTitle title="Deployment" sub="instance details" />
              <div className="space-y-3">
                {[
                  { icon: Cpu, label: "Region", value: "eu-west-1 · eu-central-1" },
                  { icon: Shield, label: "Encryption", value: "TLS 1.3 · AES-256 at rest" },
                  { icon: KeyRound, label: "Authentication", value: "SSO · MFA enforced" },
                  { icon: Bell, label: "Incident webhook", value: "configured" },
                  { icon: SlidersHorizontal, label: "Version", value: "SentinelX v1.0.0" },
                ].map((row) => (
                  <div key={row.label} className="flex items-center justify-between rounded-lg border border-border-subtle bg-white/[0.02] px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <row.icon className="h-3.5 w-3.5 text-text-muted" />
                      <span className="text-xs text-text-secondary">{row.label}</span>
                    </div>
                    <span className="mono text-[10px] text-accent-light">{row.value}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}

        {tab === "policies" && (
          <motion.div key="policies" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <SectionTitle title="Policy Builder" sub="create a custom enforcement policy" right={<Badge variant="info">Live</Badge>} />
              <div className="space-y-3">
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Policy name</label>
                  <input value={policy.name} onChange={(e) => setPolicy((p) => ({ ...p, name: e.target.value }))} placeholder="e.g. No PHI in support prompts" className="w-full rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent" />
                </div>
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Description</label>
                  <textarea value={policy.description} onChange={(e) => setPolicy((p) => ({ ...p, description: e.target.value }))} rows={2} placeholder="What data this policy protects and when it applies…" className="w-full resize-none rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent" />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="mb-1 block text-[11px] font-medium text-text-secondary">Regulation</label>
                    <select value={policy.regulation} onChange={(e) => setPolicy((p) => ({ ...p, regulation: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-2 py-2 text-xs text-text-primary outline-none focus:border-accent">
                      {REGULATIONS.map((r) => <option key={r}>{r}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-[11px] font-medium text-text-secondary">Category</label>
                    <select value={policy.category} onChange={(e) => setPolicy((p) => ({ ...p, category: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-2 py-2 text-xs text-text-primary outline-none focus:border-accent">
                      {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-[11px] font-medium text-text-secondary">Severity</label>
                    <select value={policy.severity} onChange={(e) => setPolicy((p) => ({ ...p, severity: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-2 py-2 text-xs text-text-primary outline-none focus:border-accent">
                      {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
                <button onClick={createPolicy} className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-xs font-semibold text-white shadow-glow transition-colors hover:bg-accent-light">
                  <Plus className="h-3.5 w-3.5" /> Publish policy
                </button>
                <p className="flex items-center gap-1.5 text-[10px] text-text-muted">
                  <Sparkles className="h-3 w-3 text-accent-light" /> Published policies are enforced immediately by the Policy Engine across all environments.
                </p>
                <div className="mt-4 rounded-xl border border-border-default bg-white/[0.02] p-3">
                  <p className="mb-2 text-[11px] font-semibold text-text-secondary">Quick-start templates</p>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      { name: "No PHI in support", reg: "HIPAA", cat: "Health", sev: "HIGH" },
                      { name: "Block card data", reg: "PCI DSS", cat: "Financial", sev: "CRITICAL" },
                      { name: "PII redaction", reg: "GDPR", cat: "PII", sev: "HIGH" },
                    ].map((t) => (
                      <button
                        key={t.name}
                        onClick={() => {
                          setPolicy({ name: t.name, description: `Template policy for ${t.reg} — ${t.cat} exposure.`, regulation: t.reg, category: t.cat, severity: t.sev })
                          toast({ kind: "info", title: "Template loaded", desc: `${t.name} is ready to publish.` })
                        }}
                        className="rounded-lg border border-border-default bg-white/[0.02] px-2.5 py-1.5 text-[10px] text-text-secondary transition-colors hover:border-accent/50 hover:text-accent-light"
                      >
                        {t.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
              <div className="mb-3 flex items-center justify-between">
                <SectionTitle title="Active Policies" sub={`${customPolicies.length} custom · 7 built-in packs`} />
              </div>
              <div className="space-y-2">
                {["Data Protection (GDPR)", "Employee Records (HR)", "Cardholder Data (PCI DSS)", "Protected Health Information (HIPAA)"].map((name) => (
                  <div key={name} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <ScrollText className="h-3.5 w-3.5 text-accent-light" />
                      <span className="text-xs text-text-primary">{name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="success">enabled</Badge>
                      <Toggle on onChange={() => toast({ kind: "info", title: `${name} updated`, desc: "Policy state toggled." })} />
                    </div>
                  </div>
                ))}
                {customPolicies.map((p) => (
                  <motion.div key={p.id} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="flex items-center justify-between rounded-lg border border-accent/30 bg-accent/5 px-3 py-2.5">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-3.5 w-3.5 text-accent-light" />
                        <span className="truncate text-xs font-medium text-text-primary">{p.name}</span>
                        <span className="tech-chip">{p.regulation}</span>
                      </div>
                      {p.description && <p className="mt-0.5 truncate text-[10px] text-text-muted">{p.description}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="warning">{p.severity}</Badge>
                      <button onClick={() => deletePolicy(p.id)} aria-label={`Delete policy ${p.name}`} className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-status-critical/20 hover:text-status-critical">
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </motion.div>
                ))}
                {customPolicies.length === 0 && (
                  <p className="rounded-lg border border-dashed border-border-strong py-6 text-center text-[11px] text-text-muted">No custom policies yet — use the builder to publish one.</p>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}

        {tab === "policies" && (
          <motion.div key="policies-ai" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="glass-card card-glow border-accent/20 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-accent-light" />
                <SectionTitle title="AI Policy Recommendations" sub="analysis of recent violations to suggest policy packs and controls" />
              </div>
              <button
                onClick={async () => {
                  if (aiRecsLoading) return
                  setAiRecsLoading(true)
                  try {
                    const res = await api.policyRecommend("Technology", ["GDPR"])
                    setAiRecs({ items: res.data, model: res.model, simulated: res.simulated })
                  } catch {
                    setAiRecs(null)
                  } finally {
                    setAiRecsLoading(false)
                  }
                }}
                disabled={aiRecsLoading}
                className="flex items-center gap-1.5 rounded-lg border border-border-default bg-white/[0.02] px-3 py-1.5 text-[11px] font-medium text-text-secondary transition-all hover:border-accent/50 hover:bg-accent/5 hover:text-text-primary disabled:opacity-50"
              >
                <RefreshCw className={cn("h-3 w-3", aiRecsLoading && "animate-spin")} />
                {aiRecs ? "Re-analyse" : "Analyse posture"}
              </button>
            </div>
            {aiRecsLoading && !aiRecs ? (
              <div className="mt-3 grid gap-3 md:grid-cols-3">
                {[0, 1, 2].map((i) => <div key={i} className="h-28 animate-pulse rounded-lg bg-white/[0.04]" />)}
              </div>
            ) : aiRecs ? (
              <>
                <div className="mt-3 flex items-center gap-2">
                  {aiRecs.model && <span className="mono text-[10px] text-text-muted">{aiRecs.model}</span>}
                  {aiRecs.simulated && <Badge variant="info">simulated</Badge>}
                </div>
                <div className="mt-2 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {aiRecs.items.map((r) => (
                    <div key={r.id} className="rounded-lg border border-border-default bg-white/[0.02] p-3.5">
                      <div className="flex items-center justify-between gap-2">
                        <span className={cn("rounded-md px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider",
                          r.priority === "critical" && "bg-critical text-status-critical",
                          r.priority === "high" && "bg-high text-status-high",
                          r.priority === "medium" && "bg-medium text-status-medium",
                          r.priority === "low" && "bg-low text-status-low")}>{r.priority}</span>
                        <Badge variant="outline">{r.regulation}</Badge>
                      </div>
                      <p className="mt-2 text-xs font-semibold text-text-primary">{r.pack}</p>
                      <p className="mt-1 text-[10px] leading-relaxed text-text-muted">{r.rationale}</p>
                      <button
                        onClick={() => {
                          setPolicy({ name: r.pack, description: r.action, regulation: r.regulation, category: "PII", severity: r.priority.toUpperCase() === "CRITICAL" ? "CRITICAL" : r.priority === "high" ? "HIGH" : "MEDIUM" })
                          toast({ kind: "success", title: "Recommendation applied", desc: `${r.pack} loaded into the policy builder.` })
                        }}
                        className="mt-2 flex items-center gap-1 rounded-md border border-accent/30 bg-accent/10 px-2 py-1 text-[10px] font-medium text-accent-light transition-colors hover:bg-accent/20"
                      >
                        <Plus className="h-3 w-3" /> Apply to builder
                      </button>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="mt-3 text-xs text-text-muted">Analyse recent violations to get AI-suggested policy packs and controls.</p>
            )}
          </motion.div>
        )}

        {tab === "notifications" && (
          <motion.div key="notifications" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <SectionTitle title="Notification Rules" sub="route alerts to your incident response channels" />
              <div className="space-y-3">
                {[
                  { key: "slack", label: "Slack", desc: "Send critical alerts to #security-alerts", on: notifications.slack },
                  { key: "teams", label: "Microsoft Teams", desc: "Post high-severity incidents to the SOC channel", on: notifications.teams },
                  { key: "email", label: "Email", desc: "Daily digest to security@acme-corp.com", on: notifications.email },
                  { key: "webhook", label: "Webhook", desc: "POST JSON payloads to a custom endpoint", on: notifications.webhook },
                ].map((n) => (
                  <div key={n.key} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                    <div className="flex items-center gap-3">
                      <span className={cn("flex h-8 w-8 items-center justify-center rounded-lg", n.on ? "bg-accent/15" : "bg-white/[0.03]")}>
                        <Bot className={cn("h-4 w-4", n.on ? "text-accent-light" : "text-text-muted")} />
                      </span>
                      <div>
                        <p className="text-xs font-medium text-text-primary">{n.label}</p>
                        <p className="text-[10px] text-text-muted">{n.desc}</p>
                      </div>
                    </div>
                    <Toggle on={n.on} onChange={() => setNotifications((s) => ({ ...s, [n.key as keyof typeof s]: !s[n.key as keyof typeof s] }))} label={n.label} />
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
              <SectionTitle title="Webhook Endpoint" sub="receive structured incident events" />
              <div>
                <label className="mb-1 block text-[11px] font-medium text-text-secondary">Target URL</label>
                <div className="flex gap-2">
                  <input
                    value={notifications.webhookUrl}
                    onChange={(e) => setNotifications((s) => ({ ...s, webhookUrl: e.target.value }))}
                    className="mono w-full rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent"
                  />
                  <button onClick={testWebhook} className="flex-shrink-0 rounded-lg border border-accent/40 bg-accent/10 px-3 text-xs font-semibold text-accent-light transition-colors hover:bg-accent/20">
                    Test
                  </button>
                </div>
              </div>
              <div className="mt-4">
                <p className="mb-2 text-[11px] font-medium text-text-secondary">Event payload</p>
                <pre className="mono overflow-x-auto rounded-lg border border-border-default bg-bg-secondary/60 p-3 text-[10px] leading-relaxed text-text-muted">
{`{
  "type": "incident.created",
  "id": "…",
  "riskScore": 89,
  "decision": "BLOCK",
  "timestamp": "2026-08-01T…"
}`}
                </pre>
              </div>
            </motion.div>
          </motion.div>
        )}

        {tab === "tokens" && (
          <motion.div key="tokens" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="glass-card p-5">
            {/* One-time secret reveal banner */}
            {newSecretOnce && (
              <div className="mb-5 rounded-lg border border-status-high/40 bg-status-high/10 p-4">
                <p className="text-xs font-semibold text-status-high mb-1">⚠ Copy your API key now — it will not be shown again</p>
                <p className="text-[11px] text-text-secondary mb-2">Key: <strong>{newSecretOnce.name}</strong></p>
                <div className="flex items-center gap-2">
                  <code className="mono flex-1 overflow-x-auto rounded border border-border-default bg-bg-secondary px-3 py-2 text-[11px] text-text-primary select-all">{newSecretOnce.secret}</code>
                  <button
                    onClick={() => { navigator.clipboard.writeText(newSecretOnce.secret); toast({ kind: "success", title: "Copied!", desc: "API key copied to clipboard." }) }}
                    className="flex-shrink-0 rounded-md p-2 text-text-muted transition hover:bg-white/[0.06] hover:text-text-primary"
                    aria-label="Copy secret"
                  ><Copy className="h-4 w-4" /></button>
                </div>
                <button onClick={() => setNewSecretOnce(null)} className="mt-3 text-[10px] text-text-muted underline">I have copied it — dismiss</button>
              </div>
            )}
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold">API Tokens</h3>
                <p className="text-[11px] text-text-muted">Programmatic access to the SentinelX gateway</p>
              </div>
              <button onClick={createToken} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-xs font-semibold text-white shadow-glow transition-colors hover:bg-accent-light">
                <Plus className="h-3.5 w-3.5" /> Create token
              </button>
            </div>
            <div className="space-y-2">
              {tokensLoading ? (
                <div className="py-8 text-center text-[11px] text-text-muted animate-pulse">Loading API keys…</div>
              ) : tokens.length === 0 ? (
                <p className="rounded-lg border border-dashed border-border-strong py-8 text-center text-[11px] text-text-muted">No API keys yet — click &quot;Create token&quot; to generate your first key.</p>
              ) : (
              tokens.map((t) => (
                <motion.div key={t.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] px-4 py-3">
                  <KeyRound className="h-4 w-4 text-accent-light" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-medium text-text-primary">{t.label}</p>
                      <Badge variant="outline">{t.scope}</Badge>
                    </div>
                    <p className="mono mt-0.5 text-[10px] text-text-muted">{t.prefix}••••••••</p>
                  </div>
                  <span className="text-[10px] text-text-muted">created {t.created}</span>
                  <span className="text-[10px] text-text-muted">last used {t.lastUsed}</span>
                  <button onClick={() => toast({ kind: "success", title: "Token copied", desc: `${t.prefix}•••••••• copied to clipboard.` })} aria-label={`Copy token ${t.label}`} className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-white/[0.06] hover:text-text-primary">
                    <Copy className="h-3.5 w-3.5" />
                  </button>
                  <button onClick={() => revokeToken(t.id)} aria-label={`Revoke token ${t.label}`} className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-status-critical/20 hover:text-status-critical">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </motion.div>
              ))
              )}
            </div>
          </motion.div>
        )}

        {tab === "branding" && (
          <motion.div key="branding" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <SectionTitle title="Enterprise Branding" sub="controls how SentinelX appears inside your organization" />
              <div className="space-y-3">
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Organization name</label>
                  <input value={branding.orgName} onChange={(e) => setBranding((b) => ({ ...b, orgName: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent" />
                </div>
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Accent color</label>
                  <div className="flex items-center gap-2">
                    {["#0b827a", "#0ea79c", "#3b82f6", "#8b5cf6", "#f97316", "#22c55e"].map((c) => (
                      <button
                        key={c}
                        onClick={() => setBranding((b) => ({ ...b, accent: c }))}
                        aria-label={`Accent ${c}`}
                        className={cn("h-8 w-8 rounded-lg border-2 transition-transform", branding.accent === c ? "scale-110 border-white" : "border-transparent")}
                        style={{ background: c }}
                      />
                    ))}
                    <input
                      type="color"
                      value={branding.accent}
                      onChange={(e) => setBranding((b) => ({ ...b, accent: e.target.value }))}
                      className="h-8 w-8 cursor-pointer rounded-lg border border-border-default bg-transparent"
                      aria-label="Custom accent color"
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Interface theme</p>
                    <p className="text-[10px] text-text-muted">Dark mode is recommended for SOC operations</p>
                  </div>
                  <Toggle on={branding.theme === "dark"} onChange={() => setBranding((b) => ({ ...b, theme: b.theme === "dark" ? "light" : "dark" }))} label="Dark theme" />
                </div>
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Support contact</label>
                  <input value={branding.supportEmail} onChange={(e) => setBranding((b) => ({ ...b, supportEmail: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent" />
                </div>
                <div>
                  <label className="mb-1 block text-[11px] font-medium text-text-secondary">Security footer note</label>
                  <input value={branding.footerNote} onChange={(e) => setBranding((b) => ({ ...b, footerNote: e.target.value }))} className="w-full rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent" />
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
              <SectionTitle title="Live Preview" sub="how reports and dashboards will look" />
              <div className="rounded-xl border border-border-default bg-bg-secondary/60 p-5">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg shadow-glow" style={{ background: branding.accent }}>
                    <Shield className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold" style={{ color: branding.accent }}>{branding.orgName}</p>
                    <p className="text-[10px] uppercase tracking-widest text-text-muted">AI Governance Firewall</p>
                  </div>
                </div>
                <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                  <motion.div initial={{ width: 0 }} animate={{ width: "72%" }} transition={{ duration: 0.8 }} className="h-full rounded-full" style={{ background: branding.accent }} />
                </div>
                <p className="mt-3 text-[10px] text-text-muted">Compliance score 92% · threats blocked 1,240 · uptime 99.99%</p>
                <div className="mt-4 rounded-lg border border-border-default bg-white/[0.02] p-3">
                  <p className="text-[10px] text-text-secondary">Generated protection report</p>
                  <p className="mt-1 text-[10px] text-text-muted">{branding.footerNote}</p>
                  <p className="mt-1 text-[10px] text-text-muted">Support: {branding.supportEmail}</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {tab === "export" && (
          <motion.div key="export" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <SectionTitle title="Export Formats" sub="which formats are available for reports & analytics" />
              <div className="space-y-2">
                {[
                  { key: "pdf" as const, label: "PDF", desc: "Board-ready compliance reports" },
                  { key: "csv" as const, label: "CSV", desc: "Raw analytics datasets for analysis" },
                  { key: "json" as const, label: "JSON", desc: "Machine-readable event streams" },
                  { key: "png" as const, label: "PNG", desc: "Chart snapshots for slides & docs" },
                ].map((f) => (
                  <div key={f.key} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15">
                        <FileDown className={cn("h-4 w-4", exportPrefs[f.key] ? "text-accent-light" : "text-text-muted")} />
                      </span>
                      <div>
                        <p className="text-xs font-medium text-text-primary">{f.label}</p>
                        <p className="text-[10px] text-text-muted">{f.desc}</p>
                      </div>
                    </div>
                    <Toggle on={exportPrefs[f.key]} onChange={() => setExportPrefs((s) => ({ ...s, [f.key]: !s[f.key] }))} label={f.label} />
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="space-y-4">
              <div className="glass-card p-5">
                <SectionTitle title="Scheduled Digest" sub="automated compliance & threat reports" />
                <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Delivery frequency</p>
                    <p className="text-[10px] text-text-muted">Email the security leadership digest</p>
                  </div>
                  <select value={exportPrefs.schedule} onChange={(e) => setExportPrefs((s) => ({ ...s, schedule: e.target.value }))} className="rounded-lg border border-border-default bg-bg-tertiary px-3 py-1.5 text-xs text-text-primary outline-none focus:border-accent">
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                <div className="mt-2 flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Include prompt text</p>
                    <p className="text-[10px] text-text-muted">Full prompt bodies in export payloads</p>
                  </div>
                  <Toggle on={exportPrefs.includePromptText} onChange={() => setExportPrefs((s) => ({ ...s, includePromptText: !s.includePromptText }))} label="Include prompt text" />
                </div>
                <div className="mt-2 flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                  <div>
                    <p className="text-xs font-medium text-text-primary">Include user PII</p>
                    <p className="text-[10px] text-text-muted">Names, emails, and departments (admin only)</p>
                  </div>
                  <Toggle on={exportPrefs.includeUserPii} onChange={() => setExportPrefs((s) => ({ ...s, includeUserPii: !s.includeUserPii }))} label="Include user PII" />
                </div>
              </div>

              <div className="glass-card card-glow p-5">
                <SectionTitle title="Export Policy" sub="data handling controls" />
                <div className="space-y-2">
                  {[
                    { icon: Shield, text: "All exports are recorded in the audit trail." },
                    { icon: KeyRound, text: "Exports require at minimum an Analyst role." },
                    { icon: ScrollText, text: "PII fields are redacted unless explicitly enabled." },
                  ].map((row) => (
                    <div key={row.text} className="flex items-start gap-2.5 rounded-lg bg-white/[0.02] px-3 py-2.5">
                      <row.icon className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-accent-light" />
                      <p className="text-[11px] leading-relaxed text-text-secondary">{row.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {tab === "roles" && (
          <motion.div key="roles" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="grid gap-4 lg:grid-cols-3">
            {ROLE_DEFS.map((r, i) => (
              <motion.div key={r.role} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="glass-card p-5">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-accent-light" />
                    <h3 className="text-sm font-semibold">{r.role}</h3>
                  </div>
                  <span className={cn("text-[10px] font-semibold uppercase tracking-wider", r.color)}>{i === 0 ? "full access" : i === 1 ? "elevated" : "read-only"}</span>
                </div>
                <div className="space-y-2">
                  {r.perms.map((p) => {
                    const on = rolePerms[r.role]?.[p] ?? true
                    return (
                      <div key={p} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2.5">
                        <span className="text-[11px] text-text-secondary">{p}</span>
                        <Toggle
                          on={on}
                          onChange={() =>
                            setRolePerms((prev) => {
                              const role = prev[r.role]
                              if (!role) return prev
                              return { ...prev, [r.role]: { ...role, [p]: !role[p] } }
                            })
                          }
                          label={p}
                        />
                      </div>
                    )
                  })}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
