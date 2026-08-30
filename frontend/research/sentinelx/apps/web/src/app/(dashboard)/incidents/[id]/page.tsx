"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useParams, useRouter } from "next/navigation"
import {
  AlertTriangle,
  ArrowLeft,
  Bot,
  CheckCircle2,
  ChevronDown,
  ClipboardList,
  Clock,
  Crosshair,
  FileDown,
  FileSearch,
  Fingerprint,
  Flag,
  Gavel,
  GitBranch,
  KeyRound,
  Lock,
  MemoryStick,
  MessageSquarePlus,
  Network,
  ScanSearch,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  UserCheck,
  Users,
  Wand2,
  Zap,
} from "lucide-react"
import { api, formatDate, formatTime, timeAgo, THREAT_COLORS } from "@/lib/api"
import type { AuditRecord, DetectedSecret, Incident, IncidentStatus, PolicyViolation } from "@/types"
import { Badge, DecisionBadge, RiskGauge, SeverityBadge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"
import { DecisionExplanation } from "@/components/ui/explainable-ai"
import { Skeleton } from "@/components/ui/motion"

const AGENT_LABELS: Record<string, { label: string; icon: typeof Bot; desc: string }> = {
  "inspector-agent": { label: "Inspector Agent", icon: ScanSearch, desc: "Classifies intent & data sensitivity" },
  "secret-detection-agent": { label: "Secret Detection", icon: KeyRound, desc: "30+ pattern rules scan" },
  "policy-engine": { label: "Policy Engine", icon: ShieldCheck, desc: "GDPR · HIPAA · PCI DSS · SOC 2 · ISO 27001" },
  "risk-engine": { label: "Risk Engine", icon: Zap, desc: "Live enterprise risk scoring" },
  "prompt-rewriter": { label: "Prompt Rewriter", icon: Wand2, desc: "Intent-preserving sanitisation" },
  "llm-adapter": { label: "LLM Adapter", icon: Bot, desc: "Multi-provider gateway routing" },
  "audit-logger": { label: "Audit Logger", icon: FileSearch, desc: "Tamper-evident audit record" },
  "memory-agent": { label: "Memory Agent", icon: MemoryStick, desc: "Session & behavioural context" },
}

const AGENTS = [
  { key: "inspector-agent", label: "Inspector Agent", desc: "Classified intent and estimated data sensitivity before any policy evaluation.", icon: ScanSearch },
  { key: "secret-detection-agent", label: "Secret Detection", desc: "Ran 30+ pattern rules against the prompt and matched sensitive entities.", icon: KeyRound },
  { key: "policy-engine", label: "Policy Engine", desc: "Evaluated 5 regulation packs and resolved triggering violations.", icon: ShieldCheck },
  { key: "risk-engine", label: "Risk Engine", desc: "Composited severity, exposure, and department context into a risk score.", icon: Zap },
  { key: "prompt-rewriter", label: "Prompt Rewriter", desc: "Preserved intent while removing sensitive entities from the outbound prompt.", icon: Wand2 },
  { key: "llm-adapter", label: "LLM Adapter", desc: "Routed the sanitized prompt to the configured model provider.", icon: Bot },
  { key: "audit-logger", label: "Audit Logger", desc: "Committed a tamper-evident record to the audit trail.", icon: FileSearch },
]

const STATUS_FLOW: IncidentStatus[] = ["TRIAGE", "INVESTIGATING", "CONTAINED", "RESOLVED"]

const STATUS_TONE: Record<IncidentStatus, string> = {
  TRIAGE: "border-status-critical/30 bg-status-critical/10 text-status-critical",
  INVESTIGATING: "border-status-high/30 bg-status-high/10 text-status-high",
  CONTAINED: "border-status-medium/30 bg-status-medium/10 text-status-medium",
  RESOLVED: "border-status-low/30 bg-status-low/10 text-status-low",
}

const ANALYSTS = ["Priya Sharma", "Daniel Okafor", "Sofia Reyes", "Kenji Watanabe", "Aarav Mehta", "Maya Iyer"]

function riskReasoning(rec: AuditRecord): Array<{ label: string; weight: number; detail: string }> {
  const reasons: Array<{ label: string; weight: number; detail: string }> = []
  if (rec.riskScore >= 80) reasons.push({ label: "Critical severity", weight: 40, detail: "Composite risk score exceeded the critical threshold (80+)." })
  else if (rec.riskScore >= 60) reasons.push({ label: "High severity", weight: 35, detail: "Composite risk score exceeded the high threshold (60+)." })
  else if (rec.riskScore >= 35) reasons.push({ label: "Elevated risk", weight: 30, detail: "Composite risk score above the medium threshold (35)." })
  else reasons.push({ label: "Low risk", weight: 10, detail: "Composite risk score stayed within safe bounds." })

  const secrets = (rec.secrets ?? []) as DetectedSecret[]
  if (secrets.length > 0) reasons.push({ label: "Sensitive data exposure", weight: Math.min(35, secrets.length * 8), detail: `${secrets.length} sensitive entit${secrets.length === 1 ? "y" : "ies"} matched detection patterns.` })

  const violations = (rec.violations ?? []) as PolicyViolation[]
  if (violations.length > 0) reasons.push({ label: "Policy violations", weight: Math.min(35, violations.length * 12), detail: `${violations.length} policy pack${violations.length === 1 ? "" : "s"} triggered.` })

  if (rec.threatLevel === "CRITICAL" || rec.threatLevel === "HIGH") reasons.push({ label: "Threat classification", weight: 15, detail: `Classified as ${rec.threatLevel} threat level.` })

  return reasons.sort((a, b) => b.weight - a.weight)
}

function complianceImpact(rec: AuditRecord): Array<{ regulation: string; status: string; note: string }> {
  const regulations = ["GDPR", "HIPAA", "PCI DSS", "SOC 2", "ISO 27001"]
  const violations = (rec.violations ?? []) as PolicyViolation[]
  const triggered = new Set(violations.map((v) => v.regulation))
  return regulations.map((reg) => ({
    regulation: reg,
    status: triggered.has(reg) ? "VIOLATED" : "OK",
    note: triggered.has(reg) ? `Associated policy triggered during this incident.` : `No ${reg} rule matched this request.`,
  }))
}

function recommendedAction(rec: AuditRecord): string {
  const violations = (rec.violations ?? []) as PolicyViolation[]
  if (rec.decision === "BLOCK") return violations[0]?.recommendation ?? "Prompt blocked. Review the request with the requestor and verify whether the data exposure was legitimate."
  if (rec.decision === "REWRITE") return "Prompt was sanitized before transmission. Inform the user that sensitive entities were redacted and advise against pasting credentials or PII into AI tools."
  if (rec.decision === "FLAG") return "Flagged for review. A security analyst should triage within 24 hours and confirm whether policy needs tightening."
  return "No action required. The prompt met all policy requirements and was transmitted safely."
}

const WORKFLOW_STEPS = [
  { id: "triage", label: "Triage", emoji: "🔎" },
  { id: "assign", label: "Assign", emoji: "👤" },
  { id: "investigate", label: "Investigate", emoji: "🧪" },
  { id: "contain", label: "Contain", emoji: "🛡️" },
  { id: "resolve", label: "Resolve", emoji: "✅" },
] as const

function workflowIndex(inc: Incident): number {
  if (inc.status === "RESOLVED") return 4
  if (inc.status === "CONTAINED") return 3
  if (inc.status === "INVESTIGATING") return 2
  return inc.owner ? 1 : 0
}

function workflowNext(inc: Incident): string {
  if (inc.status === "RESOLVED") return "none — runbook complete"
  if (inc.status === "CONTAINED") return "confirm closure and mark resolved"
  if (inc.status === "INVESTIGATING") return "contain the blast radius"
  if (!inc.owner) return "assign an owner"
  return "begin investigation"
}

function workflowHint(inc: Incident): string {
  if (inc.status === "RESOLVED") return "Runbook complete. SentinelX has archived the tamper-evident record and will surface similar patterns to the memory agent for future detection."
  if (inc.status === "CONTAINED") return "Blast radius contained. Confirm remediation with the owner, then close the incident — the AI recommendation panel has the final checklist."
  if (inc.status === "INVESTIGATING") return "Investigation in progress. Evidence package, MITRE ATT&CK mapping and the AI recommendation panel guide the analyst toward containment."
  if (!inc.owner) return "Waiting for assignment. SLA timer is running — assign an owner to begin the investigation phase."
  return "Owner assigned. Begin triage by reviewing the evidence package, then move to the investigation phase."
}

function DecisionGraph({ inc, rec }: { inc: Incident | null; rec: AuditRecord | null }) {
  const [open, setOpen] = useState<Record<string, boolean>>({})
  const secrets = (rec?.secrets ?? []) as DetectedSecret[]
  const violations = (rec?.violations ?? []) as PolicyViolation[]
  const triggerKey = (key: string) =>
    key === "secret-detection-agent" ? secrets.length > 0 : key === "policy-engine" ? violations.length > 0 : key === "risk-engine" ? true : key === "prompt-rewriter" ? !!rec?.rewrittenPrompt : key === "llm-adapter" ? rec?.decision !== "ALLOW" : true

  const autoExpanded = useMemo(() => {
    const first = AGENTS.find((a) => triggerKey(a.key))
    const map: Record<string, boolean> = {}
    if (first) map[first.key] = true
    return map
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rec, inc])

  useEffect(() => {
    setOpen((o) => (Object.keys(o).length ? o : autoExpanded))
  }, [autoExpanded])

  const nodes = [
    { key: "prompt", label: "Prompt", desc: `"${(inc?.prompt ?? rec?.prompt ?? "").slice(0, 90)}…"`, icon: MessageSquarePlus, active: true },
    ...AGENTS.map((a) => ({ ...a, active: triggerKey(a.key) })),
    { key: "decision", label: "Decision", desc: `${inc?.decision ?? rec?.decision ?? "ALLOW"} resolved at risk ${inc?.riskScore ?? rec?.riskScore}/100`, icon: Gavel, active: true },
  ]

  return (
    <div className="glass-card card-glow p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-accent-light" />
          <h3 className="text-sm font-semibold">Interactive Decision Graph</h3>
        </div>
        <span className="text-[11px] text-text-muted">click any node to expand its reasoning</span>
      </div>
      <div className="relative space-y-0">
        {nodes.map((n, i) => {
          const Icon = n.icon
          const isOpen = !!open[n.key]
          const isLast = i === nodes.length - 1
          return (
            <div key={n.key}>
              <button
                onClick={() => setOpen((o) => ({ ...o, [n.key]: !o[n.key] }))}
                className={cn(
                  "group flex w-full items-center gap-3 rounded-lg border px-3.5 py-3 text-left transition-all duration-200",
                  isOpen ? "border-accent/40 bg-accent/[0.06]" : "border-border-default bg-white/[0.02] hover:border-border-strong",
                )}
              >
                <span className={cn("flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg", n.active ? "bg-accent/15 text-accent-light" : "bg-white/[0.04] text-text-muted")}>
                  <Icon className="h-4 w-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={cn("text-xs font-semibold", n.active ? "text-text-primary" : "text-text-muted")}>{n.label}</span>
                    <span className={cn("mono text-[9px]", n.active ? "text-accent-light" : "text-text-muted")}>step {i + 1}</span>
                  </div>
                  <p className="mt-0.5 truncate text-[10px] text-text-muted">{n.desc}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={n.active ? "info" : "outline"}>{n.active ? "Executed" : "Passed"}</Badge>
                  <ChevronDown className={cn("h-3.5 w-3.5 text-text-muted transition-transform duration-200", isOpen && "rotate-180")} />
                </div>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="mx-3.5 mb-2 mt-1 rounded-lg border border-border-subtle bg-bg-secondary/40 p-3.5">
                      <p className="text-[11px] leading-relaxed text-text-secondary">
                        {n.key === "prompt"
                          ? "The raw prompt entered the gateway and was captured for analysis."
                          : n.key === "decision"
                            ? `The pipeline resolved to ${inc?.decision ?? rec?.decision ?? "ALLOW"} — this incident was generated from the outcome.`
                            : n.desc}
                      </p>
                      {(n.key === "secret-detection-agent" && secrets.length > 0) && (
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {secrets.slice(0, 4).map((s, si) => (
                            <span key={si} className="mono rounded bg-status-critical/10 px-2 py-0.5 text-[10px] text-status-critical">{s.label}</span>
                          ))}
                        </div>
                      )}
                      {(n.key === "policy-engine" && violations.length > 0) && (
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {violations.slice(0, 4).map((v, vi) => (
                            <span key={vi} className="rounded bg-status-high/10 px-2 py-0.5 text-[10px] text-status-high">{v.policyName}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              {!isLast && <div className="mx-auto h-3 w-px bg-border-default" />}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function RiskTrend({ inc }: { inc: Incident }) {
  const data = inc.riskTrend
  const max = Math.max(...data.map((d) => d.score), 1)
  const W = 480
  const H = 90
  const step = W / Math.max(data.length - 1, 1)
  const points = data.map((d, i) => `${i * step},${H - (d.score / max) * (H - 10) - 4}`).join(" ")
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Incident risk trend">
        <defs>
          <linearGradient id="rtGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={`0,${H} ${points} ${W},${H}`} fill="url(#rtGrad)" />
        <motion.polyline points={points} fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1 }} />
      </svg>
      <div className="mt-1 flex justify-between text-[9px] text-text-muted">
        <span>{data[0]?.t}</span>
        <span>{data[data.length - 1]?.t}</span>
      </div>
    </div>
  )
}

function Timeline({ inc }: { inc: Incident }) {
  const KIND_TONE: Record<string, string> = {
    SYSTEM: "bg-accent-light",
    ACTION: "bg-status-high",
    NOTE: "bg-status-medium",
    ALERT: "bg-status-critical",
  }
  return (
    <div className="relative space-y-4 pl-5">
      <div className="absolute bottom-1 left-[5px] top-1 w-px bg-border-default" />
      {inc.timeline.map((t, i) => (
        <motion.div key={t.id} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="relative">
          <span className={cn("absolute -left-5 top-1.5 h-[11px] w-[11px] rounded-full border-2 border-bg-primary", KIND_TONE[t.kind] ?? "bg-text-muted")} />
          <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-medium text-text-primary">{t.event}</p>
              <span className="mono text-[9px] text-text-muted">{timeAgo(t.at)}</span>
            </div>
            <p className="mt-1 text-[11px] leading-relaxed text-text-muted">{t.detail}</p>
            <p className="mt-1.5 text-[9px] text-text-muted/70">by {t.actor} · {t.kind}</p>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

function NotesThread({ inc, onChange }: { inc: Incident; onChange: (i: Incident) => void }) {
  const [body, setBody] = useState("")
  const [author, setAuthor] = useState("Aarav Mehta")
  const [sending, setSending] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const submit = async () => {
    if (!body.trim() || sending) return
    setSending(true)
    setErr(null)
    try {
      const updated = await api.incidentNote(inc.id, body.trim(), author)
      onChange(updated)
      setBody("")
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to post note — check the API connection.")
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Your name"
          className="w-36 rounded-lg border border-border-default bg-bg-secondary/60 px-3 py-2 text-[11px] text-text-primary outline-none transition-colors focus:border-accent/60"
        />
        <input
          value={body}
          onChange={(e) => setBody(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Add an investigation note… (Enter to post)"
          className="flex-1 rounded-lg border border-border-default bg-bg-secondary/60 px-3 py-2 text-xs text-text-primary outline-none transition-colors focus:border-accent/60"
        />
        <button
          onClick={submit}
          disabled={!body.trim() || sending}
          className="flex items-center gap-1.5 rounded-lg border border-accent/40 bg-accent/10 px-3.5 py-2 text-xs font-semibold text-accent-light transition-all hover:bg-accent/20 disabled:opacity-40"
        >
          <Send className="h-3.5 w-3.5" /> {sending ? "Posting…" : "Post"}
        </button>
      </div>
      {err && (
        <p className="flex items-center gap-1.5 text-[11px] text-status-critical" role="alert">
          <AlertTriangle className="h-3 w-3" /> {err}
        </p>
      )}
      <div className="space-y-2.5">
        {inc.notes.map((n) => (
          <motion.div key={n.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 text-xs font-medium text-text-primary">
                <UserCheck className="h-3 w-3 text-accent-light" /> {n.author}
              </span>
              <span className="text-[9px] text-text-muted">{timeAgo(n.createdAt)}</span>
            </div>
            <p className="mt-1 text-[11px] leading-relaxed text-text-secondary">{n.body}</p>
          </motion.div>
        ))}
        {inc.notes.length === 0 && <p className="py-4 text-center text-xs text-text-muted">No notes yet — start the investigation thread.</p>}
      </div>
    </div>
  )
}

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [inc, setInc] = useState<Incident | null>(null)
  const [rec, setRec] = useState<AuditRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [now, setNow] = useState(Date.now())
  const [busy, setBusy] = useState(false)
  const [actionErr, setActionErr] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!id) return
    try {
      const [i, r] = await Promise.all([
        api.incident(id).catch(() => null),
        api.auditById(id).catch(() => null),
      ])
      setInc(i)
      setRec(r)
      if (!i && !r) setError(true)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])

  const slaMs = useMemo(() => {
    if (!inc) return null
    const deadline = new Date(inc.createdAt).getTime() + inc.slaMinutes * 60000
    return Math.max(0, deadline - now)
  }, [inc, now])

  const slaLabel = useMemo(() => {
    if (!slaMs || inc?.status === "RESOLVED") return "—"
    if (slaMs === 0) return "BREACHED"
    const h = Math.floor(slaMs / 3600000)
    const m = Math.floor((slaMs % 3600000) / 60000)
    const s = Math.floor((slaMs % 60000) / 1000)
    return h > 0 ? `${h}h ${m}m` : `${m}m ${s.toString().padStart(2, "0")}s`
  }, [slaMs, inc?.status])

  const act = async (fn: () => Promise<Incident>) => {
    setBusy(true)
    setActionErr(null)
    try {
      setInc(await fn())
    } catch (e) {
      setActionErr(e instanceof Error ? e.message : "Update failed — check the API connection.")
    } finally {
      setBusy(false)
    }
  }

  const downloadReport = () => {
    const payload = inc
      ? { product: "SentinelX AI Governance Firewall", type: "Incident response report", ...inc, generatedAt: new Date().toISOString() }
      : rec
        ? {
            product: "SentinelX AI Governance Firewall",
            type: "Incident investigation report",
            incidentId: rec.id,
            decision: rec.decision,
            riskScore: rec.riskScore,
            threatLevel: rec.threatLevel,
            timestamp: rec.timestamp,
            prompt: rec.prompt,
            rewrittenPrompt: rec.rewrittenPrompt,
            secrets: rec.secrets,
            violations: rec.violations,
            generatedAt: new Date().toISOString(),
          }
        : null
    if (!payload) return
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `sentinelx-incident-${(inc?.id ?? rec?.id ?? "report").slice(0, 8)}.json`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="mb-2"><Skeleton className="h-4 w-24" /></div>
        <Skeleton className="h-40 rounded-xl" />
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
        <Skeleton className="h-72 rounded-xl" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <ShieldAlert className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">Incident not found or unreachable</p>
        <button onClick={() => router.back()} className="tech-chip cursor-pointer hover:border-accent">
          <ArrowLeft className="h-3 w-3" /> Go back
        </button>
      </div>
    )
  }

  const secrets = (rec?.secrets ?? []) as DetectedSecret[]
  const violations = (rec?.violations ?? []) as PolicyViolation[]
  const reasons = rec ? riskReasoning(rec) : []
  const maxWeight = Math.max(...reasons.map((r) => r.weight), 1)
  const displayId = inc?.id ?? rec?.id ?? ""
  const displayDecision = inc?.decision ?? rec?.decision ?? "ALLOW"
  const displayRisk = inc?.riskScore ?? rec?.riskScore ?? 0
  const displayThreat = inc ? (inc.riskScore >= 80 ? "CRITICAL" : inc.riskScore >= 60 ? "HIGH" : inc.riskScore >= 35 ? "MEDIUM" : "LOW") : rec?.threatLevel ?? "LOW"
  const displayUser = rec?.user

  return (
    <div className="space-y-6">
      <div className="mb-2">
        <button onClick={() => router.back()} className="flex items-center gap-1.5 text-xs font-medium text-text-muted transition-colors hover:text-accent-light">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to incident list
        </button>
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("glass-card p-6", displayRisk >= 80 && "glass-card-accent border-status-critical/30")}
      >
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="flex items-center gap-5">
            <RiskGauge score={displayRisk} size="lg" />
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="mono text-[11px] text-text-muted">{displayId}</span>
                <h1 className="text-lg font-semibold tracking-tight">{inc?.title ?? "Incident Investigation"}</h1>
                <DecisionBadge decision={displayDecision} />
              </div>
              <p className="mt-1 text-xs text-text-muted">
                {inc ? `${inc.department} · risk ${inc.riskScore}/100 · ` : ""}
                {rec ? `${rec.llmProvider ?? "gateway"} · ` : ""}
                {formatDate((inc?.createdAt ?? rec?.timestamp ?? "") as string)} at {formatTime((inc?.createdAt ?? rec?.timestamp ?? "") as string)} ({timeAgo((inc?.createdAt ?? rec?.timestamp ?? "") as string)})
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <span className={cn("mono text-sm font-bold", THREAT_COLORS[displayThreat])}>{displayRisk}/100 · {displayThreat}</span>
                {inc && (
                  <>
                    <span className="text-text-muted">·</span>
                    <SeverityBadge severity={inc.severity} />
                    <Badge variant="outline" className={STATUS_TONE[inc.status]}>{inc.status}</Badge>
                    {inc.escalated && <Badge variant="danger">ESCALATED</Badge>}
                    {inc.owner ? (
                      <Badge variant="info"><UserCheck className="mr-1 h-3 w-3" /> {inc.owner}</Badge>
                    ) : (
                      <Badge variant="warning">UNASSIGNED</Badge>
                    )}
                  </>
                )}
                {displayUser && (
                  <>
                    <span className="text-text-muted">·</span>
                    <span className="text-xs text-text-secondary">{displayUser.name} {displayUser.department ? `· ${displayUser.department}` : ""}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-2 text-[11px] text-text-muted">
              <Lock className="h-3 w-3" />
              Tamper-evident audit record
            </div>
            <button
              onClick={downloadReport}
              className="flex items-center gap-2 rounded-lg border border-accent/40 bg-accent/10 px-3.5 py-2 text-xs font-semibold text-accent-light transition-all hover:bg-accent/20"
            >
              <FileDown className="h-3.5 w-3.5" /> Download report
            </button>
          </div>
        </div>
      </motion.div>

      {/* Incident response controls */}
      {inc && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <ClipboardList className="h-4 w-4 text-accent-light" /> Incident Response
            </h3>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-wider text-text-muted">Owner</span>
                <select
                  value={inc.owner ?? ""}
                  onChange={(e) => act(() => api.incidentAssign(inc.id, e.target.value))}
                  disabled={busy}
                  className={cn(
                    "rounded-lg border border-border-default bg-bg-secondary/60 px-2.5 py-1.5 text-[11px] text-text-primary outline-none transition-colors focus:border-accent/60",
                    !inc.owner && "text-status-warning",
                  )}
                >
                  <option value="">Unassigned</option>
                  {ANALYSTS.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] uppercase tracking-wider text-text-muted">Status</span>
                {STATUS_FLOW.map((st) => (
                  <button
                    key={st}
                    onClick={() => act(() => api.incidentStatus(inc.id, st))}
                    disabled={busy}
                    className={cn(
                      "rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold transition-all",
                      inc.status === st ? "border-accent/60 bg-accent/15 text-accent-light" : "border-border-default text-text-muted hover:border-border-strong hover:text-text-secondary",
                    )}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {actionErr && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-status-critical/30 bg-status-critical/10 px-3 py-2 text-[11px] text-status-critical" role="alert">
              <AlertTriangle className="h-3.5 w-3.5" /> {actionErr}
            </div>
          )}

          {/* SLA bar */}
          <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs">
                <Clock className={cn("h-4 w-4", slaMs !== null && slaMs === 0 && inc.status !== "RESOLVED" ? "text-status-critical animate-pulse" : "text-text-muted")} />
                <span className="text-text-secondary">Response SLA</span>
                <span className="mono font-semibold text-text-primary">{slaLabel}</span>
                <span className="text-[10px] text-text-muted">of {inc.slaMinutes}m for {inc.severity} severity</span>
              </div>
              {inc.escalated && <Badge variant="danger">escalated to incident commander</Badge>}
            </div>
            <div className="mt-2.5 h-2 overflow-hidden rounded-full bg-white/[0.05]">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${inc.status === "RESOLVED" ? 100 : Math.max(0, Math.min(100, ((slaMs ?? 0) / (inc.slaMinutes * 60000)) * 100))}%` }}
                transition={{ duration: 0.8 }}
                className={cn("h-full rounded-full", slaMs !== null && slaMs === 0 && inc.status !== "RESOLVED" ? "bg-status-critical" : (slaMs ?? 0) / (inc.slaMinutes * 60000) < 0.25 ? "bg-status-high" : (slaMs ?? 0) / (inc.slaMinutes * 60000) < 0.6 ? "bg-status-medium" : "bg-status-low")}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Resolution workflow */}
      {inc && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <GitBranch className="h-4 w-4 text-accent-light" /> Resolution Workflow
            </h3>
            <span className="text-[11px] text-text-muted">{inc.status === "RESOLVED" ? "Runbook complete" : `Next action: ${workflowNext(inc)}`}</span>
          </div>
          <div className="flex items-start">
            {WORKFLOW_STEPS.map((step, i) => {
              const idx = WORKFLOW_STEPS.indexOf(step)
              const done = idx < workflowIndex(inc)
              const current = idx === workflowIndex(inc)
              const last = i === WORKFLOW_STEPS.length - 1
              return (
                <div key={step.id} className={cn("flex flex-col items-center", !last && "flex-1")}>
                  <div className="flex w-full items-center">
                    <div className={cn("h-0.5 flex-1", i === 0 ? "opacity-0" : done || current ? "bg-accent/50" : "bg-white/[0.06]")} />
                    <motion.div
                      animate={current ? { scale: [1, 1.18, 1] } : {}}
                      transition={current ? { repeat: Infinity, duration: 1.6, ease: "easeInOut" } : {}}
                      className={cn(
                        "flex h-9 w-9 items-center justify-center rounded-full border text-[11px] font-semibold",
                        done && "border-accent/60 bg-accent/20 text-accent-light",
                        current && "border-accent bg-accent/25 text-accent-light shadow-[var(--shadow-glow)]",
                        !done && !current && "border-border-strong bg-bg-secondary/60 text-text-muted",
                      )}
                    >
                      {done ? <CheckCircle2 className="h-4 w-4" /> : <span>{step.emoji}</span>}
                    </motion.div>
                    <div className={cn("h-0.5 flex-1", last ? "opacity-0" : idx < workflowIndex(inc) ? "bg-accent/50" : "bg-white/[0.06]")} />
                  </div>
                  <p className={cn("mt-2 text-[10px] font-medium", current ? "text-accent-light" : done ? "text-text-secondary" : "text-text-muted")}>
                    {step.label}
                  </p>
                </div>
              )
            })}
          </div>
          <p className="mt-4 rounded-lg border border-accent/15 bg-accent/[0.04] px-3 py-2 text-[11px] leading-relaxed text-text-secondary">
            <Sparkles className="mr-1.5 inline h-3 w-3 text-accent-light" />
            {workflowHint(inc)}
          </p>
        </motion.div>
      )}

      {/* Prompt comparison */}
      {rec && (
        <div className="grid gap-4 lg:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-sm font-semibold">
                <AlertTriangle className="h-4 w-4 text-status-critical" /> Original Prompt
              </h3>
              <Badge variant="outline">{secrets.length} sensitive entit{secrets.length === 1 ? "y" : "ies"}</Badge>
            </div>
            <HighlightedPrompt text={rec.prompt} secrets={secrets} />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-sm font-semibold">
                <Wand2 className="h-4 w-4 text-accent-light" /> Sanitized / Final Prompt
              </h3>
              {rec.rewrittenPrompt ? <Badge variant="warning">Rewritten</Badge> : <Badge variant="success">Unchanged</Badge>}
            </div>
            {rec.rewrittenPrompt ? (
              <div className="rounded-xl border border-accent/25 bg-accent/5 p-4 text-sm leading-relaxed text-text-primary">{rec.rewrittenPrompt}</div>
            ) : (
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-secondary">{rec.prompt}</div>
            )}
            <p className="mt-3 flex items-center gap-1.5 text-[11px] text-accent-light">
              <Sparkles className="h-3.5 w-3.5" />
              {rec.rewrittenPrompt ? "Intent preserved · sensitive entities removed before reaching the model" : "Prompt reached the model as-is — no sensitive entities present"}
            </p>
          </motion.div>
        </div>
      )}

      {/* AI recommendation + risk trend + evidence */}
      <div className="grid gap-4 lg:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
          <div className="mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-accent-light" />
            <h3 className="text-sm font-semibold">AI Recommendation</h3>
          </div>
          <div className="rounded-xl border border-accent/25 bg-accent/5 p-4">
            <p className="text-xs leading-relaxed text-text-secondary">{inc?.aiRecommendation ?? (rec ? recommendedAction(rec) : "No recommendation available.")}</p>
          </div>
          {rec && (
            <div className="mt-4 mb-3 flex items-center gap-2">
              <Gavel className="h-4 w-4 text-status-medium" />
              <h3 className="text-sm font-semibold">Compliance Impact</h3>
            </div>
          )}
          {rec && (
            <div className="space-y-2">
              {complianceImpact(rec).map((c) => (
                <div key={c.regulation} className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                  <span className="text-xs font-medium text-text-primary">{c.regulation}</span>
                  <Badge variant={c.status === "OK" ? "success" : "danger"}>{c.status}</Badge>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {inc && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
            <div className="mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-status-high" />
              <h3 className="text-sm font-semibold">Risk Trend</h3>
            </div>
            <RiskTrend inc={inc} />
            <div className="mt-4">
              <div className="mb-2 flex items-center gap-2">
                <Crosshair className="h-4 w-4 text-status-critical" />
                <h3 className="text-sm font-semibold">MITRE ATT&CK Mapping</h3>
              </div>
              <div className="space-y-2">
                {inc.mitreAttack.map((m) => (
                  <div key={m.id} className="rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                    <div className="flex items-center justify-between">
                      <span className="mono text-[11px] font-semibold text-status-critical">{m.id}</span>
                      <span className="tech-chip">{m.tactic}</span>
                    </div>
                    <p className="mt-1 text-[11px] text-text-secondary">{m.name}</p>
                  </div>
                ))}
                {inc.mitreAttack.length === 0 && <p className="py-3 text-center text-xs text-text-muted">No ATT&CK techniques mapped</p>}
              </div>
            </div>
          </motion.div>
        )}

        {inc && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="glass-card p-5">
            <div className="mb-3 flex items-center gap-2">
              <Fingerprint className="h-4 w-4 text-status-medium" />
              <h3 className="text-sm font-semibold">Evidence Package</h3>
            </div>
            <div className="space-y-2">
              {inc.evidence.map((e) => (
                <div key={e.id} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-medium text-text-primary">{e.label}</span>
                    <span className="tech-chip">{e.kind}</span>
                  </div>
                  <p className="mono mt-1 truncate text-[10px] text-text-muted">{e.value}</p>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <div className="mb-2 flex items-center gap-2">
                <Users className="h-4 w-4 text-accent-light" />
                <h3 className="text-sm font-semibold">Related</h3>
              </div>
              <div className="mb-2 flex flex-wrap gap-1.5">
                {inc.relatedPolicies.map((p) => (
                  <span key={p} className="rounded bg-status-high/10 px-2 py-1 text-[10px] text-status-high">{p}</span>
                ))}
                {inc.relatedPolicies.length === 0 && <span className="text-[10px] text-text-muted">No related policies</span>}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {inc.relatedUsers.map((u) => (
                  <span key={u} className="rounded bg-accent/10 px-2 py-1 text-[10px] text-accent-light">{u}</span>
                ))}
                {inc.relatedUsers.length === 0 && <span className="text-[10px] text-text-muted">No related users</span>}
              </div>
            </div>
            {inc.relatedPrompts && inc.relatedPrompts.length > 0 && (
              <div className="mt-4 border-t border-border-subtle pt-4">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="flex items-center gap-2 text-sm font-semibold">
                    <MessageSquarePlus className="h-4 w-4 text-status-info" /> Related Prompts
                  </h3>
                  <span className="text-[10px] text-text-muted">contextual traffic</span>
                </div>
                <div className="space-y-2">
                  {inc.relatedPrompts.map((rp) => (
                    <motion.div
                      key={rp.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                      className="rounded-lg border border-border-default bg-white/[0.02] p-2.5"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate text-[10px] text-text-muted">{rp.user}</span>
                        <div className="flex shrink-0 items-center gap-1.5">
                          <span className={cn("mono text-[10px] font-semibold", rp.risk >= 80 ? "text-status-critical" : rp.risk >= 50 ? "text-status-high" : rp.risk >= 30 ? "text-status-medium" : "text-status-low")}>
                            {rp.risk}
                          </span>
                          <DecisionBadge decision={rp.decision} />
                        </div>
                      </div>
                      <p className="mt-1 truncate text-[10px] text-text-secondary">{rp.prompt}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Timeline + notes */}
      {inc && (
        <div className="grid gap-4 lg:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
            <div className="mb-4 flex items-center gap-2">
              <Clock className="h-4 w-4 text-accent-light" />
              <h3 className="text-sm font-semibold">Incident Timeline</h3>
            </div>
            <Timeline inc={inc} />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card p-5">
            <div className="mb-4 flex items-center gap-2">
              <MessageSquarePlus className="h-4 w-4 text-status-info" />
              <h3 className="text-sm font-semibold">Investigation Notes</h3>
            </div>
            <NotesThread inc={inc} onChange={setInc} />
          </motion.div>
        </div>
      )}

      {/* Interactive decision graph */}
      <DecisionGraph inc={inc} rec={rec} />

      {/* Explainable AI */}
      {rec && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent-light" />
              <h3 className="text-sm font-semibold">Explainable AI — Why this decision</h3>
            </div>
            <span className="text-[11px] text-text-muted">full transparency into every agent's reasoning</span>
          </div>
          <DecisionExplanation result={rec} />
        </motion.div>
      )}

      {/* Risk reasoning */}
      {rec && reasons.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
          <div className="mb-3 flex items-center gap-2">
            <Zap className="h-4 w-4 text-status-high" />
            <h3 className="text-sm font-semibold">Risk Reasoning</h3>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {reasons.map((r, i) => (
              <motion.div key={r.label} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-text-primary">{r.label}</span>
                  <span className="mono text-text-secondary">+{r.weight} pts</span>
                </div>
                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(r.weight / maxWeight) * 100}%` }}
                    transition={{ duration: 0.7, delay: 0.2 + i * 0.06 }}
                    className="h-full rounded-full bg-gradient-to-r from-status-high to-status-critical"
                  />
                </div>
                <p className="mt-1.5 text-[11px] leading-relaxed text-text-muted">{r.detail}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Agent decisions timeline */}
      {rec && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-accent-light" />
              <h3 className="text-sm font-semibold">Agent Decision Timeline</h3>
            </div>
            <span className="text-[11px] text-text-muted">the agents that inspected this request</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(AGENT_LABELS).map(([key, meta], i) => {
              const Icon = meta.icon
              const triggered = key === "secret-detection-agent" ? secrets.length > 0 : key === "policy-engine" ? violations.length > 0 : key === "risk-engine"
              const status = triggered ? "ACTIVE" : "PASS"
              return (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className={cn("rounded-lg border p-3.5", status === "ACTIVE" ? "border-accent/30 bg-accent/5" : "border-border-default bg-white/[0.02]")}
                >
                  <div className="flex items-center justify-between">
                    <Icon className={cn("h-4 w-4", status === "ACTIVE" ? "text-accent-light" : "text-text-muted")} />
                    {status === "ACTIVE" ? <CheckCircle2 className="h-4 w-4 text-status-low" /> : <Flag className="h-3.5 w-3.5 text-text-muted" />}
                  </div>
                  <p className="mt-2 text-xs font-medium text-text-primary">{meta.label}</p>
                  <p className="mt-0.5 line-clamp-2 text-[10px] text-text-muted">{meta.desc}</p>
                  <div className="mt-2">
                    <Badge variant={status === "ACTIVE" ? "info" : "outline"}>{status === "ACTIVE" ? "Matched" : "Passed"}</Badge>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Matched patterns */}
      {rec && secrets.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
          <div className="mb-3 flex items-center gap-2">
            <Fingerprint className="h-4 w-4 text-status-critical" />
            <h3 className="text-sm font-semibold">Matched Patterns</h3>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {secrets.map((s, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                <div className="flex items-center justify-between">
                  <SeverityBadge severity={s.severity} />
                  <span className="text-[10px] text-text-muted">conf {(s.confidence * 100).toFixed(0)}%</span>
                </div>
                <p className="mt-2 text-xs font-medium text-text-primary">{s.label}</p>
                <p className="mono mt-1 truncate rounded bg-white/[0.04] px-2 py-1 text-[10px] text-status-critical">{s.match}</p>
                <p className="mono mt-1 truncate rounded bg-accent/10 px-2 py-1 text-[10px] text-accent-light">→ {s.redacted}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Policy violations */}
      {rec && violations.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
          <div className="mb-3 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-status-high" />
            <h3 className="text-sm font-semibold">Policy Violations</h3>
          </div>
          <div className="space-y-3">
            {violations.map((v, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }} className="rounded-lg border border-border-default bg-white/[0.02] p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={v.severity} />
                    <span className="text-xs font-medium text-text-primary">{v.policyName}</span>
                  </div>
                  <span className="tech-chip">{v.regulation} · {v.category} · rule {v.ruleId}</span>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-text-secondary">{v.reason}</p>
                <p className="mt-1.5 flex items-start gap-1.5 text-[11px] text-accent-light">
                  <Sparkles className="mt-0.5 h-3 w-3 flex-shrink-0" />
                  {v.recommendation}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}

function HighlightedPrompt({ text, secrets }: { text: string; secrets: DetectedSecret[] }) {
  if (secrets.length === 0) {
    return (
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-secondary">
        {text}
      </div>
    )
  }
  const parts: React.ReactNode[] = []
  let last = 0
  for (const s of secrets) {
    const start = s.position.start
    const end = s.position.end
    if (start > last) parts.push(<span key={`t-${last}`}>{text.slice(last, start)}</span>)
    parts.push(
      <mark key={`s-${start}`} className="rounded bg-status-critical/20 px-1 py-0.5 text-status-critical">
        {text.slice(start, end)}
      </mark>,
    )
    last = end
  }
  if (last < text.length) parts.push(<span key="tail">{text.slice(last)}</span>)
  return (
    <div className="rounded-xl border border-border-default bg-white/[0.02] p-4 text-sm leading-relaxed text-text-primary">
      {parts}
    </div>
  )
}
