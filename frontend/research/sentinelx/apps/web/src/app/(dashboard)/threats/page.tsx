"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { AlertTriangle, ChevronDown, ExternalLink, ShieldAlert, Sparkles } from "lucide-react"
import { api, timeAgo, THREAT_COLORS } from "@/lib/api"
import type { AuditRecord, DetectedSecret, PolicyViolation } from "@/types"
import { Badge, DecisionBadge, PageHeader, SeverityBadge } from "@/components/ui/primitives"
import { CountUp } from "@/components/ui/motion"
import { cn } from "@/lib/utils"
import Link from "next/link"

export default function ThreatsPage() {
  const [events, setEvents] = useState<AuditRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.audit({ limit: 40 })
      setEvents(d.records.filter((r) => r.riskScore >= 15))
    } catch {
      setEvents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [load])

  const counts = useMemo(
    () => ({
      critical: events.filter((e) => e.riskScore >= 80).length,
      high: events.filter((e) => e.riskScore >= 60 && e.riskScore < 80).length,
      blocked: events.filter((e) => e.decision === "BLOCK").length,
      rewritten: events.filter((e) => e.decision === "REWRITE").length,
    }),
    [events],
  )

  const severityTone = (ev: AuditRecord) =>
    ev.riskScore >= 80
      ? { border: "border-l-status-critical/60", icon: "text-status-critical", bg: "bg-critical" }
      : ev.riskScore >= 60
        ? { border: "border-l-status-high/60", icon: "text-status-high", bg: "bg-high" }
        : ev.riskScore >= 35
          ? { border: "border-l-status-medium/60", icon: "text-status-medium", bg: "bg-medium" }
          : { border: "border-l-status-info/60", icon: "text-status-info", bg: "bg-info" }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Threat Timeline"
        description="Every prompt that raised risk, in chronological order — with the detection chain, policy triggers, and the final decision."
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Critical events", value: counts.critical, cls: "text-status-critical" },
          { label: "High events", value: counts.high, cls: "text-status-high" },
          { label: "Blocked", value: counts.blocked, cls: "text-status-critical" },
          { label: "Rewritten", value: counts.rewritten, cls: "text-status-high" },
        ].map((s) => (
          <div key={s.label} className="glass-card card-glow p-4">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">{s.label}</p>
            <CountUp value={s.value} className={`mono mt-1.5 text-2xl font-semibold ${s.cls}`} />
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {loading && <p className="py-12 text-center text-sm text-text-muted">Loading threat timeline…</p>}
        {!loading && events.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-16">
            <ShieldAlert className="h-8 w-8 text-status-low" />
            <p className="text-sm text-text-secondary">No threats detected. The perimeter is quiet.</p>
          </div>
        )}
        {events.map((ev, i) => {
          const tone = severityTone(ev)
          const violations = (ev.violations ?? []) as PolicyViolation[]
          const secrets = (ev.secrets ?? []) as DetectedSecret[]
          const policies = (ev.policiesTriggered as string[]) ?? []
          const isOpen = expanded === ev.id
          return (
            <motion.div
              key={ev.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: Math.min(i * 0.04, 0.6) }}
              className={cn("glass-card card-glow overflow-hidden border-l-2", tone.border)}
            >
              <button onClick={() => setExpanded(isOpen ? null : ev.id)} className="flex w-full items-center gap-4 p-4 text-left">
                <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", tone.bg)}>
                  <AlertTriangle className={cn("h-4 w-4", tone.icon)} />
                </div>
                <div className="flex items-center gap-3">
                  <div>
                    <p className={cn("mono text-sm font-semibold", THREAT_COLORS[ev.threatLevel])}>{ev.riskScore}</p>
                    <p className="text-[10px] uppercase tracking-wider text-text-muted">{ev.threatLevel}</p>
                  </div>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm text-text-primary">{ev.prompt}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <span className="text-[11px] text-text-muted">{ev.user?.name ?? "Unknown"} · {timeAgo(ev.timestamp)}</span>
                    <span className="text-[11px] text-text-muted">·</span>
                    <span className="text-[11px] text-text-muted">{ev.llmProvider ?? "gateway"}</span>
                    {secrets.slice(0, 3).map((s, j) => (
                      <SeverityBadge key={j} severity={s.severity} />
                    ))}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <DecisionBadge decision={ev.decision} />
                  <span className="text-[10px] text-text-muted">
                    {policies.slice(0, 2).join(", ") || "no policy"}
                  </span>
                  <Link
                    href={`/incidents/${ev.id}`}
                    className="flex items-center gap-1 rounded-md border border-border-default px-2 py-0.5 text-[10px] font-medium text-accent-light transition-all hover:border-accent/50 hover:bg-accent/10"
                  >
                    Investigate <ExternalLink className="h-2.5 w-2.5" />
                  </Link>
                </div>
                <ChevronDown className={cn("h-4 w-4 text-text-muted transition-transform duration-300", isOpen && "rotate-180")} />
              </button>

              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className="overflow-hidden"
                  >
                    <div className="border-t border-border-subtle bg-bg-secondary/50 px-5 py-4">
                      <div className="grid gap-4 lg:grid-cols-2">
                        {violations.length > 0 && (
                          <div>
                            <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Policy violations</p>
                            <div className="space-y-2">
                              {violations.map((v, j) => (
                                <div key={j} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                                  <div className="flex flex-wrap items-center gap-2">
                                    <SeverityBadge severity={v.severity} />
                                    <span className="text-xs font-medium text-text-primary">{v.policyName}</span>
                                    <Badge variant="outline">{v.regulation}</Badge>
                                  </div>
                                  <p className="mt-1.5 text-[11px] leading-relaxed text-text-secondary">{v.reason}</p>
                                  <p className="mt-1 flex items-start gap-1 text-[10px] text-accent-light">
                                    <Sparkles className="mt-0.5 h-3 w-3 flex-shrink-0" />
                                    {v.recommendation}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        <div>
                          <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Detected secrets</p>
                          {secrets.length > 0 ? (
                            <div className="space-y-2">
                              {secrets.map((s, j) => (
                                <div key={j} className="flex items-center justify-between gap-3 rounded-lg border border-border-default bg-white/[0.02] px-3 py-2">
                                  <div className="flex items-center gap-2">
                                    <SeverityBadge severity={s.severity} />
                                    <span className="text-[11px] text-text-secondary">{s.label}</span>
                                  </div>
                                  <span className="mono max-w-[200px] truncate rounded bg-white/[0.04] px-2 py-0.5 text-[10px] text-status-critical">
                                    {s.match}
                                  </span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-[11px] text-text-muted">No secrets matched — risk driven by policy or intent.</p>
                          )}
                          <div className="mt-3 flex flex-wrap gap-2">
                            <span className="tech-chip">pipeline {ev.promptHash?.slice(0, 8)}</span>
                            <span className="tech-chip">id {ev.id.slice(0, 8)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
