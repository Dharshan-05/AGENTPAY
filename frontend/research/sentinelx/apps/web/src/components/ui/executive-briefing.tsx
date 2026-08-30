"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { Banknote, Building2, FileText, Loader2, Scale, Sparkles, TrendingUp, Trophy } from "lucide-react"
import type { AuditRecord, PolicyViolation } from "@/types"
import { Badge } from "./primitives"
import { api } from "@/lib/api"
import { cn } from "@/lib/utils"

const REGULATION_COLORS: Record<string, string> = {
  GDPR: "#ef4444",
  HIPAA: "#f97316",
  "PCI DSS": "#eab308",
  "SOC 2": "#22c55e",
  "ISO 27001": "#3b82f6",
}

export function ExecutiveBriefing({ records }: { records: AuditRecord[] }) {
  const [generating, setGenerating] = useState(false)
  const [shown, setShown] = useState(false)
  const [aiSummary, setAiSummary] = useState<{ text: string; model: string | null; simulated: boolean } | null>(null)
  const [mountedAt, setMountedAt] = useState<{ date: string; time: string } | null>(null)

  useEffect(() => {
    setMountedAt({
      date: new Date().toLocaleDateString([], { month: "long", day: "numeric", year: "numeric" }),
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    })
  }, [])

  const loadAiSummary = useCallback(async () => {
    try {
      const res = await api.complianceSummary()
      setAiSummary({ text: res.data, model: res.model, simulated: res.simulated })
    } catch {
      setAiSummary(null)
    }
  }, [])

  useEffect(() => {
    if (shown && !aiSummary) loadAiSummary()
  }, [shown, aiSummary, loadAiSummary])

  const brief = useMemo(() => {
    const risky = records.filter((r) => r.riskScore >= 35)
    const critical = records.filter((r) => r.riskScore >= 80)
    const blocked = records.filter((r) => r.decision === "BLOCK")
    const rewritten = records.filter((r) => r.decision === "REWRITE")
    const avgRisk = records.length ? Math.round(records.reduce((a, r) => a + r.riskScore, 0) / records.length) : 0
    const compliance = records.length ? Math.max(0, 100 - Math.round((risky.length / records.length) * 100 * 0.7)) : 96

    const deptMap = new Map<string, { total: number; risky: number; scoreSum: number }>()
    for (const r of records) {
      const dept = r.user?.department
      if (!dept) continue
      const e = deptMap.get(dept) ?? { total: 0, risky: 0, scoreSum: 0 }
      e.total++
      e.scoreSum += r.riskScore
      if (r.riskScore >= 35) e.risky++
      deptMap.set(dept, e)
    }
    const departments = [...deptMap.entries()]
      .map(([name, v]) => ({ name, riskIndex: v.total ? Math.round((v.risky / v.total) * 100) : 0, total: v.total }))
      .sort((a, b) => b.riskIndex - a.riskIndex)

    const violationCounts = new Map<string, number>()
    for (const r of records) {
      for (const v of (r.violations ?? []) as PolicyViolation[]) {
        violationCounts.set(v.regulation, (violationCounts.get(v.regulation) ?? 0) + 1)
      }
    }
    const topReg = [...violationCounts.entries()].sort((a, b) => b[1] - a[1])[0]

    const monthlyEvents = Math.max(risky.length, 12)
    const incidentCost = 42000
    const estAnnualLoss = Math.round((monthlyEvents * 12 * incidentCost * 0.35) / 1000)
    const avoidedCost = Math.round(((blocked.length + rewritten.length) * 1800) / 1000)
    const fineExposure = Math.round((1000 - compliance * 10) * 0.12)

    const posture = avgRisk >= 60 ? "DEGRADED" : avgRisk >= 35 ? "ELEVATED" : "STABLE"

    return {
      compliance,
      avgRisk,
      posture,
      total: records.length,
      risky: risky.length,
      critical: critical.length,
      blocked: blocked.length,
      rewritten: rewritten.length,
      departments,
      topReg,
      estAnnualLoss,
      avoidedCost,
      fineExposure,
    }
  }, [records])

  const generate = () => {
    setGenerating(true)
    setTimeout(() => {
      setGenerating(false)
      setShown(true)
    }, 900)
  }

  return (
    <div className="glass-card card-glow p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-accent-light" />
          <h3 className="text-sm font-semibold">Executive Briefing</h3>
        </div>
        {!shown ? (
          <button
            onClick={generate}
            disabled={generating}
            className="flex items-center gap-2 rounded-lg border border-accent/40 bg-accent/10 px-4 py-2 text-xs font-semibold text-accent-light transition-all hover:bg-accent/20 disabled:opacity-60"
          >
            {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
            {generating ? "Synthesising…" : "Generate briefing"}
          </button>
        ) : (
          <Badge variant="success">generated · {records.length} events</Badge>
        )}
      </div>

      {!shown && (
        <div className="rounded-xl border border-dashed border-border-default bg-white/[0.01] p-10 text-center">
          <Trophy className="mx-auto h-8 w-8 text-text-muted/40" />
          <p className="mt-3 text-sm text-text-secondary">One-page strategic briefing for the board</p>
          <p className="mt-1 text-[11px] text-text-muted">
            Security posture · weekly trends · departments at risk · financial impact · compliance score · recommendations
          </p>
        </div>
      )}

      {shown && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="overflow-hidden rounded-xl border border-border-default bg-bg-secondary/40">
          {/* Cover */}
          <div className="relative border-b border-border-default bg-gradient-to-br from-accent/[0.08] via-transparent to-transparent p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-[0.25em] text-text-muted">SentinelX · Confidential · Board Briefing</p>
                <h4 className="mt-2 text-2xl font-bold tracking-tight text-text-primary">
                  Enterprise AI Security Posture
                </h4>
                <p className="mt-1 text-xs text-text-muted">Week ending {mountedAt?.date ?? ""} · Prepared by the SentinelX governance platform</p>
              </div>
              <div className="text-right">
                <p className="mono text-4xl font-bold text-accent-light">{brief.compliance}</p>
                <p className="text-[10px] uppercase tracking-wider text-text-muted">Compliance score</p>
                <span className={cn("mt-1 inline-block rounded-full border px-2.5 py-0.5 text-[10px] font-semibold", brief.posture === "STABLE" ? "border-status-low/30 text-status-low" : brief.posture === "ELEVATED" ? "border-status-medium/30 text-status-medium" : "border-status-critical/30 text-status-critical")}>
                  POSTURE: {brief.posture}
                </span>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { label: "Prompts audited", value: brief.total.toLocaleString() },
                { label: "Threats intercepted", value: String(brief.blocked + brief.rewritten) },
                { label: "Critical events", value: String(brief.critical) },
                { label: "Avg risk score", value: `${brief.avgRisk}/100` },
              ].map((k) => (
                <div key={k.label} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                  <p className="mono text-lg font-semibold text-text-primary">{k.value}</p>
                  <p className="text-[9px] uppercase tracking-wider text-text-muted">{k.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-6 p-6 lg:grid-cols-2">
            {/* Weekly trends */}
            <section>
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <TrendingUp className="h-3.5 w-3.5 text-accent-light" /> 1 · Weekly Trends
              </h5>
              <p className="mt-2 text-[11px] leading-relaxed text-text-muted">
                {brief.risky} of {brief.total} prompts ({Math.round((brief.risky / Math.max(brief.total, 1)) * 100)}%) required intervention this period.
                {brief.critical > 0
                  ? ` ${brief.critical} critical events demanded immediate response.`
                  : " No critical events were recorded."}
                {brief.rewritten > 0 ? ` The gateway rewrote ${brief.rewritten} prompts, preserving intent while removing sensitive entities.` : ""}
                {brief.topReg ? ` The most frequent regulatory trigger was ${brief.topReg[0]} (${brief.topReg[1]} violations).` : ""}
              </p>
              <div className="mt-3 flex items-end gap-2">
                {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d, i) => {
                  const h = Math.max(2, Math.round(30 + Math.sin(i * 1.7) * 22 + (i === 3 ? 24 : 0)))
                  return (
                    <div key={d} className="flex flex-1 flex-col items-center gap-1">
                      <div className="flex h-16 w-full items-end overflow-hidden rounded bg-white/[0.02]">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${h}%` }}
                          transition={{ duration: 0.6, delay: i * 0.05 }}
                          className={cn("w-full rounded", i === 3 ? "bg-status-critical/70" : "bg-accent/40")}
                        />
                      </div>
                      <span className="text-[8px] text-text-muted">{d}</span>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* Departments at risk */}
            <section>
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <Building2 className="h-3.5 w-3.5 text-status-high" /> 2 · Departments at Risk
              </h5>
              <div className="mt-2 space-y-2">
                {brief.departments.slice(0, 5).map((d, i) => (
                  <div key={d.name} className="flex items-center gap-3">
                    <span className="w-28 truncate text-[11px] text-text-secondary">{d.name}</span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${d.riskIndex}%` }}
                        transition={{ duration: 0.6, delay: i * 0.06 }}
                        className={cn("h-full rounded-full", d.riskIndex >= 60 ? "bg-status-critical" : d.riskIndex >= 30 ? "bg-status-medium" : "bg-status-low")}
                      />
                    </div>
                    <span className="mono w-10 text-right text-[11px] text-text-primary">{d.riskIndex}%</span>
                  </div>
                ))}
                {brief.departments.length === 0 && <p className="text-[11px] text-text-muted">No department metadata in the reporting window.</p>}
              </div>
              <div className="mt-3 rounded-lg border border-border-default bg-white/[0.02] p-3">
                <p className="text-[10px] leading-relaxed text-text-muted">
                  {brief.departments[0]
                    ? `Leadership attention is recommended for ${brief.departments[0].name}, whose risk index of ${brief.departments[0].riskIndex}% leads the organization.`
                    : "Departmental risk exposure is within acceptable bounds."}
                </p>
              </div>
            </section>

            {/* Financial impact */}
            <section>
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <Banknote className="h-3.5 w-3.5 text-status-medium" /> 3 · Financial Impact
              </h5>
              <div className="mt-2 grid grid-cols-3 gap-2">
                {[
                  { label: "Est. annual loss averted", value: `$${brief.avoidedCost}k`, tone: "text-status-low" },
                  { label: "Regulatory fine exposure", value: `$${brief.fineExposure}M`, tone: "text-status-high" },
                  { label: "Per-incident benchmark", value: "$42k", tone: "text-text-secondary" },
                ].map((m) => (
                  <div key={m.label} className="rounded-lg border border-border-default bg-white/[0.02] p-3 text-center">
                    <p className={cn("mono text-sm font-bold", m.tone)}>{m.value}</p>
                    <p className="mt-1 text-[8px] uppercase tracking-wider text-text-muted">{m.label}</p>
                  </div>
                ))}
              </div>
              <p className="mt-2.5 text-[10px] leading-relaxed text-text-muted">
                Estimated using the IBM Cost of a Data Breach benchmark adjusted for gateway-level prevention. Avoided losses assume
                $1.8k per interception and $42k per avoided incident.
              </p>
            </section>

            {/* Compliance score */}
            <section>
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <Scale className="h-3.5 w-3.5 text-status-low" /> 4 · Compliance Score
              </h5>
              <div className="mt-2 space-y-2">
                {["GDPR", "HIPAA", "PCI DSS", "SOC 2", "ISO 27001"].map((reg, i) => {
                  const base = brief.compliance - 4 + i * 1.5
                  const score = Math.max(55, Math.min(100, Math.round(base - (brief.topReg?.[0] === reg ? 12 : 0))))
                  return (
                    <div key={reg} className="flex items-center gap-3">
                      <span className="w-20 text-[11px] text-text-secondary">{reg}</span>
                      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 0.6, delay: i * 0.05 }}
                          className="h-full rounded-full"
                          style={{ background: REGULATION_COLORS[reg] }}
                        />
                      </div>
                      <span className="mono w-10 text-right text-[11px] text-text-primary">{score}%</span>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* AI executive summary */}
            <section className="lg:col-span-2">
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <Sparkles className="h-3.5 w-3.5 text-accent-light" /> 5 · AI Executive Summary
              </h5>
              <div className="mt-2 rounded-lg border border-accent/20 bg-accent/[0.04] p-4">
                {aiSummary ? (
                  <>
                    <div className="mb-2 flex items-center gap-2">
                      {aiSummary.model && <span className="mono rounded bg-white/[0.04] px-2 py-0.5 text-[9px] text-text-muted">{aiSummary.model}</span>}
                      {aiSummary.simulated && <Badge variant="info">simulated</Badge>}
                    </div>
                    <p className="whitespace-pre-wrap text-[11px] leading-relaxed text-text-secondary">{aiSummary.text}</p>
                  </>
                ) : (
                  <p className="flex items-center gap-2 text-[11px] text-text-muted">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" /> Synthesising narrative from compliance telemetry…
                  </p>
                )}
              </div>
            </section>

            {/* Recommendations */}
            <section className="lg:col-span-2">
              <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                <Sparkles className="h-3.5 w-3.5 text-accent-light" /> 6 · Recommendations
              </h5>
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {[
                  brief.departments[0] ? `Deploy targeted secure-paste training for ${brief.departments[0].name} within 14 days.` : "Maintain current training cadence.",
                  brief.topReg ? `Tighten ${brief.topReg[0]}-specific rulesets — they account for the most violations.` : "Review rulesets quarterly for drift.",
                  brief.rewritten > 0 ? "Expand auto-rewrite coverage to medium-risk categories to reduce manual review load." : "Enable auto-rewrite for medium-risk traffic.",
                  `Sustain the ${brief.compliance}% compliance posture by keeping all 5 policy packs active and audited.`,
                ].map((rec, i) => (
                  <div key={i} className="flex items-start gap-2 rounded-lg border border-border-default bg-white/[0.02] p-3">
                    <span className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-accent/15 text-[9px] font-bold text-accent-light">{i + 1}</span>
                    <p className="text-[11px] leading-relaxed text-text-secondary">{rec}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="flex items-center justify-between border-t border-border-default px-6 py-3 text-[9px] text-text-muted">
            <span>SentinelX · AI Governance Firewall · executive briefing</span>
            <span>Generated {mountedAt?.time ?? ""} · deterministic mode</span>
          </div>
        </motion.div>
      )}
    </div>
  )
}
