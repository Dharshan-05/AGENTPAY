"use client"

import { memo, useCallback, useEffect, useMemo, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import {
  Activity,
  ChevronDown,
  Fingerprint,
  Gavel,
  GitBranch,
  Radar,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Waypoints,
  Zap,
} from "lucide-react"
import { api } from "@/lib/api"
import type { ExplainDecision, ExplainStats } from "@/types"
import { Badge, DecisionBadge, PageHeader, SeverityBadge } from "@/components/ui/primitives"
import { Skeleton } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

export const MemoDecisionGraph = memo(function DecisionGraph({ decision }: { decision: ExplainDecision }) {
  const W = 320
  const H = 170
  const agents = decision.agentContributions.filter((a) => a.contribution > 0)
  const gap = W / (agents.length + 1)

  return (
    <div className="relative overflow-hidden rounded-lg border border-border-default bg-bg-secondary/40">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Animated decision graph">
        <defs>
          <linearGradient id="edgeGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#0ea79c" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#0ea79c" stopOpacity="0.8" />
          </linearGradient>
        </defs>
        {agents.map((_, i) => {
          const x = gap * (i + 1)
          const y = 60 + (i % 2 === 0 ? -18 : 18)
          const xNext = gap * (i + 2)
          const yNext = 60 + ((i + 1) % 2 === 0 ? -18 : 18)
          return (
            <motion.line
              key={`edge-${i}`}
              x1={x}
              y1={y}
              x2={i === agents.length - 1 ? W - 24 : xNext}
              y2={i === agents.length - 1 ? H - 26 : yNext}
              stroke="url(#edgeGrad)"
              strokeWidth={1.5}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.7 }}
              transition={{ duration: 0.9, delay: 0.3 + i * 0.12 }}
            />
          )
        })}
        {agents.map((a, i) => {
          const x = gap * (i + 1)
          const y = 60 + (i % 2 === 0 ? -18 : 18)
          return (
            <motion.g
              key={a.agent}
              initial={{ opacity: 0, scale: 0.6 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.12, type: "spring", stiffness: 300, damping: 22 }}
            >
              <circle cx={x} cy={y} r={13} fill="rgba(11,130,122,0.15)" stroke="#0ea79c" strokeWidth={1.5} />
              <circle cx={x} cy={y} r={4} fill={a.status === "TRIGGERED" ? "#f97316" : "#0ea79c"} />
              <text x={x} y={y + 28} textAnchor="middle" fill="#a1a1aa" fontSize="7" fontWeight="600">
                {a.agent.split(" ")[0]}
              </text>
            </motion.g>
          )
        })}
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>
          <rect x={W - 66} y={H - 40} width={52} height={28} rx={6} fill={decision.decision === "BLOCK" ? "rgba(239,68,68,0.15)" : decision.decision === "REWRITE" ? "rgba(249,115,22,0.15)" : "rgba(34,197,94,0.15)"} stroke="rgba(255,255,255,0.1)" />
          <text x={W - 40} y={H - 22} textAnchor="middle" fill="#fafafa" fontSize="9" fontWeight="700">
            {decision.decision}
          </text>
        </motion.g>
      </svg>
    </div>
  )
})

function ExpandableDecisionCard({ decision, index }: { decision: ExplainDecision; index: number }) {
  const [open, setOpen] = useState(index === 0)
  const [aiReasoning, setAiReasoning] = useState<{ text: string; model: string | null; simulated: boolean } | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const maxRisk = useMemo(() => Math.max(...decision.riskFactors.map((f) => f.weight), 1), [decision])

  const loadAiReasoning = useCallback(async () => {
    if (aiReasoning || aiLoading) return
    setAiLoading(true)
    try {
      const res = await api.aiReasoning(decision.id)
      setAiReasoning({ text: res.data, model: res.model, simulated: res.simulated })
    } catch {
      setAiReasoning(null)
    } finally {
      setAiLoading(false)
    }
  }, [aiReasoning, aiLoading, decision.id])

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className={cn(
        "overflow-hidden rounded-xl border transition-colors",
        open ? "border-accent/40 bg-accent/[0.03]" : "border-border-default bg-white/[0.02] hover:border-border-strong",
      )}
    >
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span
          className={cn(
            "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-[10px] font-semibold",
            decision.decision === "BLOCK"
              ? "bg-critical text-status-critical"
              : decision.decision === "REWRITE"
                ? "bg-high text-status-high"
                : decision.decision === "FLAG"
                  ? "bg-medium text-status-medium"
                  : "bg-low text-status-low",
          )}
        >
          {String(index + 1).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="truncate text-xs font-medium text-text-primary">{decision.prompt}</p>
          </div>
          <p className="mt-0.5 flex items-center gap-2 text-[10px] text-text-muted">
            <span>{decision.department}</span>
            <span>·</span>
            <span className="mono">{decision.riskScore}/100</span>
            <span>·</span>
            <span>{decision.confidence}% confidence</span>
          </p>
        </div>
        <DecisionBadge decision={decision.decision} />
        <motion.span animate={{ rotate: open ? 180 : 0 }} className="text-text-muted">
          <ChevronDown className="h-4 w-4" />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="space-y-4 border-t border-border-subtle p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                {/* Animated decision graph */}
                <div>
                  <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-accent-light">
                    <Waypoints className="h-3 w-3" /> Agent contribution graph
                  </p>
                  <MemoDecisionGraph decision={decision} />
                  <div className="mt-2 grid grid-cols-2 gap-1.5">
                    {decision.agentContributions.map((a) => (
                      <div key={a.agent} className="flex items-center gap-1.5 rounded-md bg-white/[0.02] px-2 py-1 text-[9px]">
                        <span className={cn("h-1.5 w-1.5 flex-shrink-0 rounded-full", a.status === "TRIGGERED" ? "bg-status-high" : "bg-status-low")} />
                        <span className="truncate text-text-secondary">{a.agent.split(" ")[0]}</span>
                        <span className="mono ml-auto text-text-muted">{a.confidence}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Risk + policy contribution */}
                <div className="space-y-4">
                  <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                    <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-status-high">
                      <Activity className="h-3 w-3" /> Risk contribution
                    </p>
                    <div className="space-y-2">
                      {decision.riskFactors.map((f) => (
                        <div key={f.label}>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-text-primary">{f.label}</span>
                            <span className="mono text-text-secondary">+{Math.round(f.weight)}</span>
                          </div>
                          <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${(f.weight / maxRisk) * 100}%` }}
                              transition={{ duration: 0.7 }}
                              className={cn("h-full rounded-full bg-gradient-to-r", f.tone)}
                            />
                          </div>
                          <p className="mt-1 text-[10px] leading-relaxed text-text-muted">{f.detail}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {decision.policyFactors.length > 0 && (
                    <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                      <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-status-medium">
                        <Gavel className="h-3 w-3" /> Policy contribution
                      </p>
                      <div className="space-y-1.5">
                        {decision.policyFactors.slice(0, 3).map((p, i) => (
                          <div key={i} className="flex items-center gap-2 rounded-md bg-white/[0.02] px-2 py-1.5">
                            <SeverityBadge severity={p.severity} />
                            <span className="min-w-0 flex-1 truncate text-[10px] text-text-secondary">{p.policyName}</span>
                            <span className="mono text-[9px] text-text-muted">{p.regulation}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Reasoning timeline */}
              <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-accent-light">
                  <GitBranch className="h-3 w-3" /> Timeline of reasoning
                </p>
                <div className="space-y-0">
                  {decision.reasoningTimeline.map((step, i) => (
                    <div key={step.step}>
                      <div className="flex items-start gap-2.5">
                        <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent/10 text-[9px] font-semibold text-accent-light">
                          {i + 1}
                        </span>
                        <div>
                          <p className="text-[11px] font-medium text-text-primary">{step.step}</p>
                          <p className="text-[10px] text-text-muted">{step.detail}</p>
                        </div>
                      </div>
                      {i < decision.reasoningTimeline.length - 1 && <div className="ml-[10px] h-3 w-px bg-border-strong" />}
                    </div>
                  ))}
                </div>
              </div>

              {/* Final recommendation */}
              <div className="rounded-lg border border-status-low/25 bg-low p-3">
                <p className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-status-low">
                  <Zap className="h-3 w-3" /> Final recommendation
                </p>
                <p className="text-[11px] leading-relaxed text-text-secondary">{decision.recommendation}</p>
                <button
                  onClick={loadAiReasoning}
                  disabled={aiLoading || aiReasoning != null}
                  className="mt-2 flex items-center gap-1.5 rounded-md border border-accent/30 bg-accent/10 px-2.5 py-1 text-[10px] font-medium text-accent-light transition-all hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Sparkles className="h-3 w-3" />
                  {aiLoading ? "Generating AI reasoning…" : aiReasoning ? "AI reasoning" : "Explain with AI"}
                </button>
                <AnimatePresence>
                  {aiReasoning && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-3 rounded-md border border-accent/20 bg-bg-secondary/50 p-3">
                        <div className="mb-1.5 flex items-center gap-2">
                          <Sparkles className="h-3 w-3 text-accent-light" />
                          <span className="text-[9px] font-semibold uppercase tracking-wider text-accent-light">AI narrative</span>
                          {aiReasoning.model && <span className="mono text-[9px] text-text-muted">{aiReasoning.model}</span>}
                          {aiReasoning.simulated && <span className="rounded bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-text-muted">simulated</span>}
                        </div>
                        <p className="whitespace-pre-wrap text-[11px] leading-relaxed text-text-secondary">{aiReasoning.text}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function ExplainabilityPage() {
  const [stats, setStats] = useState<ExplainStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.explain()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 20000)
    return () => clearInterval(t)
  }, [load])

  const filtered = useMemo(
    () => (filter ? stats?.decisions.filter((d) => d.decision === filter) ?? [] : stats?.decisions ?? []),
    [stats, filter],
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-72" />
            <Skeleton className="h-4 w-80" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-64 rounded-xl" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <Radar className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">Explainability engine unreachable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      </div>
    )
  }

  const s = stats.summary
  const avgConfidence = stats.decisions.length
    ? Math.round(stats.decisions.reduce((a, d) => a + d.confidence, 0) / stats.decisions.length)
    : 0

  const FILTERS: Array<{ label: string; value: string | null; tone: string }> = [
    { label: "All", value: null, tone: "text-text-secondary" },
    { label: "BLOCK", value: "BLOCK", tone: "text-status-critical" },
    { label: "REWRITE", value: "REWRITE", tone: "text-status-high" },
    { label: "FLAG", value: "FLAG", tone: "text-status-medium" },
    { label: "ALLOW", value: "ALLOW", tone: "text-status-low" },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Explainability Center"
        description="Every decision, fully explained — which agents contributed, what drove the risk score, which policies fired, and how the recommendation was reached."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="info">audit-driven</Badge>
            <Badge variant="success">transparent AI</Badge>
          </div>
        }
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        {[
          { label: "Decisions explained", value: s.total, icon: Sparkles, tone: "text-accent-light" },
          { label: "Blocked", value: s.blocked, icon: ShieldAlert, tone: "text-status-critical" },
          { label: "Rewritten", value: s.rewritten, icon: Activity, tone: "text-status-high" },
          { label: "Avg risk", value: `${s.avgRisk}/100`, icon: Radar, tone: "text-status-medium" },
          { label: "Avg confidence", value: `${avgConfidence}%`, icon: Fingerprint, tone: "text-status-low" },
        ].map((c, i) => (
          <motion.div key={c.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card card-glow p-4">
            <c.icon className={cn("h-4 w-4", c.tone)} />
            <p className="mt-2 text-[10px] uppercase tracking-wider text-text-muted">{c.label}</p>
            <p className={cn("mono mt-1 text-2xl font-semibold", c.tone)}>{c.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.label}
            onClick={() => setFilter(f.value)}
            aria-pressed={filter === f.value}
            className={cn(
              "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[11px] font-medium transition-all",
              filter === f.value ? "border-accent/50 bg-accent/10 text-accent-light shadow-glow" : "border-border-default bg-white/[0.02] text-text-secondary hover:border-border-strong",
            )}
          >
            <span className={cn("h-1.5 w-1.5 rounded-full", f.tone)} />
            {f.label}
            <span className="mono text-[9px] text-text-muted">
              {f.value === null ? stats.decisions.length : stats.decisions.filter((d) => d.decision === f.value).length}
            </span>
          </button>
        ))}
      </div>

      {/* Confidence + decision distribution */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="glass-card card-glow p-5 lg:col-span-2">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <ShieldCheck className="h-4 w-4 text-accent-light" /> Decision confidence distribution
          </h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {stats.decisions.slice(0, 8).map((d, i) => (
              <motion.div
                key={d.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.04 }}
                className="rounded-lg border border-border-default bg-white/[0.02] p-3 text-center"
              >
                <div className="relative mx-auto h-16 w-16">
                  <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="42"
                      fill="none"
                      stroke={d.confidence >= 90 ? "#0ea79c" : d.confidence >= 80 ? "#3b82f6" : "#eab308"}
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${(d.confidence / 100) * 264} 264`}
                      initial={{ strokeDasharray: "0 264" }}
                      animate={{ strokeDasharray: `${(d.confidence / 100) * 264} 264` }}
                      transition={{ duration: 0.9, delay: i * 0.05 }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="mono text-sm font-bold text-text-primary">{d.confidence}</span>
                  </div>
                </div>
                <p className="mt-2 truncate text-[10px] text-text-muted">{d.department}</p>
                <div className="mt-1 flex justify-center">
                  <DecisionBadge decision={d.decision} />
                </div>
              </motion.div>
            ))}
          </div>
          {stats.decisions.length === 0 && (
            <p className="rounded-lg border border-dashed border-border-default px-3 py-6 text-center text-xs text-text-muted">
              No decisions to analyze yet — run a scan to generate explainable decisions
            </p>
          )}
        </div>

        <div className="glass-card card-glow p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Gavel className="h-4 w-4 text-accent-light" /> Decision mix
          </h3>
          <div className="space-y-3">
            {[
              { label: "Blocked", count: s.blocked, color: "bg-status-critical" },
              { label: "Rewritten", count: s.rewritten, color: "bg-status-high" },
              { label: "Flagged", count: s.flagged, color: "bg-status-medium" },
              { label: "Allowed", count: s.allowed, color: "bg-status-low" },
            ].map((row, i) => {
              const pct = s.total ? Math.round((row.count / s.total) * 100) : 0
              return (
                <div key={row.label}>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-text-secondary">{row.label}</span>
                    <span className="mono text-text-muted">{row.count} · {pct}%</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.7, delay: 0.1 + i * 0.06 }}
                      className={cn("h-full rounded-full", row.color)}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Expandable decision cards */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">
            Decision explorer <span className="ml-1 text-[10px] font-normal text-text-muted">expand any decision for the full reasoning chain</span>
          </h3>
          <Badge variant="outline">{filtered.length} shown</Badge>
        </div>
        <AnimatePresence>
          {filtered.map((d, i) => (
            <ExpandableDecisionCard key={d.id} decision={d} index={i} />
          ))}
        </AnimatePresence>
        {filtered.length === 0 && (
          <p className="rounded-xl border border-dashed border-border-strong py-10 text-center text-xs text-text-muted">No decisions match this filter.</p>
        )}
      </div>
    </div>
  )
}
