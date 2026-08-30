"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { AlertTriangle, ArrowRight, Clock, Gauge, ShieldAlert, Siren, UserCheck, Users } from "lucide-react"
import { api, timeAgo } from "@/lib/api"
import type { Incident, IncidentStatus } from "@/types"
import { Badge, PageHeader, SeverityBadge } from "@/components/ui/primitives"
import { CountUp, Skeleton } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const STATUS_BG: Record<IncidentStatus, string> = {
  TRIAGE: "border-status-critical/30 bg-status-critical/10 text-status-critical",
  INVESTIGATING: "border-status-high/30 bg-status-high/10 text-status-high",
  CONTAINED: "border-status-medium/30 bg-status-medium/10 text-status-medium",
  RESOLVED: "border-status-low/30 bg-status-low/10 text-status-low",
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[] | null>(null)
  const [stats, setStats] = useState<{ open: number; critical: number; breached: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ severity?: string; status?: string }>({})
  const [now, setNow] = useState(Date.now())

  const load = useCallback(async () => {
    try {
      const d = await api.incidents(filter)
      setIncidents(d.incidents)
      setStats(d.stats)
    } catch {
      setIncidents([])
      setStats({ open: 0, critical: 0, breached: 0 })
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    load()
    const t = setInterval(load, 15000)
    return () => clearInterval(t)
  }, [load])

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])

  const slaRemaining = useCallback(
    (inc: Incident) => {
      const deadline = new Date(inc.createdAt).getTime() + inc.slaMinutes * 60000
      return Math.max(0, Math.round((deadline - now) / 60000))
    },
    [now],
  )

  const totals = useMemo(
    () => ({
      open: stats?.open ?? 0,
      critical: stats?.critical ?? 0,
      breached: stats?.breached ?? 0,
    }),
    [stats],
  )

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incident Response Center"
        description="Enterprise-grade incident management — severity, owners, SLA timers, evidence, and MITRE ATT&CK mapping."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="danger">{totals.open} open</Badge>
            <Badge variant="warning">{totals.critical} critical</Badge>
            {totals.breached > 0 && <Badge variant="danger">{totals.breached} SLA breached</Badge>}
          </div>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Open incidents", value: totals.open, icon: Siren, tone: "text-status-critical", suffix: "" },
          { label: "Critical severity", value: totals.critical, icon: AlertTriangle, tone: "text-status-high", suffix: "" },
          { label: "SLA breached", value: totals.breached, icon: Clock, tone: "text-status-medium", suffix: "" },
          { label: "Avg risk", value: incidents && incidents.length ? Math.round(incidents.reduce((a, i) => a + i.riskScore, 0) / incidents.length) : 0, icon: Gauge, tone: "text-accent-light", suffix: "/100" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="glass-card p-4">
            <div className="flex items-center gap-2">
              <s.icon className={cn("h-4 w-4", s.tone)} />
              <p className="text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
            </div>
            <CountUp value={s.value} suffix={s.suffix} className={cn("mono mt-1.5 text-2xl font-semibold", s.tone)} />
          </motion.div>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] text-text-muted">Filter:</span>
        {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((sev) => (
          <button
            key={sev}
            onClick={() => setFilter((f) => ({ ...f, severity: f.severity === sev ? undefined : sev }))}
            aria-pressed={filter.severity === sev}
            className={cn(
              "tech-chip cursor-pointer",
              filter.severity === sev && "border-status-critical/50 bg-status-critical/10 text-status-critical",
            )}
          >
            {sev}
          </button>
        ))}
        <span className="mx-1 h-4 w-px bg-border-default" />
        {(["TRIAGE", "INVESTIGATING", "CONTAINED", "RESOLVED"] as const).map((st) => (
          <button
            key={st}
            onClick={() => setFilter((f) => ({ ...f, status: f.status === st ? undefined : st }))}
            aria-pressed={filter.status === st}
            className={cn(
              "tech-chip cursor-pointer",
              filter.status === st && "border-accent/50 bg-accent/10 text-accent-light",
            )}
          >
            {st}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      ) : incidents && incidents.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-border-default bg-white/[0.02] py-16">
          <ShieldAlert className="h-8 w-8 text-status-low" />
          <p className="text-sm text-text-secondary">No incidents match this filter</p>
          <p className="text-[11px] text-text-muted">Clear the filters or scan a risky prompt to generate an incident.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {incidents?.map((inc, i) => {
            const remaining = slaRemaining(inc)
            const breached = remaining === 0 && inc.status !== "RESOLVED"
            const slaPct = breached ? 100 : Math.min(100, Math.round((remaining / inc.slaMinutes) * 100))
            return (
              <motion.div
                key={inc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  "group flex flex-wrap items-center gap-4 rounded-xl border bg-white/[0.02] p-4 transition-all duration-200 hover:border-border-strong hover:bg-white/[0.04]",
                  breached ? "border-status-critical/40" : "border-border-default",
                )}
              >
                <div className="flex min-w-0 flex-1 items-center gap-4">
                  <SeverityBadge severity={inc.severity} />
                  <div className="min-w-0">
                    <Link href={`/incidents/${inc.id}`} className="flex items-center gap-2">
                      <span className="mono text-[11px] text-text-muted">{inc.id}</span>
                      <span className="truncate text-sm font-medium text-text-primary transition-colors group-hover:text-accent-light">{inc.title}</span>
                    </Link>
                    <p className="mt-0.5 flex items-center gap-2 text-[10px] text-text-muted">
                      <span>{inc.department}</span>
                      <span>·</span>
                      <span>{timeAgo(inc.createdAt)}</span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        {inc.owner ? <UserCheck className="h-3 w-3 text-accent-light" /> : <Users className="h-3 w-3" />}
                        {inc.owner ?? "Unassigned"}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="flex w-44 items-center gap-2">
                  <Clock className={cn("h-3.5 w-3.5 flex-shrink-0", breached ? "text-status-critical animate-pulse" : "text-text-muted")} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className={breached ? "text-status-critical" : "text-text-muted"}>SLA</span>
                      <span className={cn("mono", breached ? "text-status-critical" : remaining <= 30 ? "text-status-high" : "text-text-secondary")}>
                        {inc.status === "RESOLVED" ? "done" : breached ? "BREACHED" : `${remaining}m`}
                      </span>
                    </div>
                    <div className="mt-1 h-1 overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${inc.status === "RESOLVED" ? 100 : slaPct}%` }}
                        transition={{ duration: 0.7 }}
                        className={cn("h-full rounded-full", breached ? "bg-status-critical" : slaPct < 25 ? "bg-status-high" : slaPct < 60 ? "bg-status-medium" : "bg-status-low")}
                      />
                    </div>
                  </div>
                </div>

                <div className="mono flex w-20 items-center gap-1 text-[11px] text-text-secondary">
                  <Gauge className="h-3 w-3 text-text-muted" />
                  {inc.riskScore}
                </div>

                <Badge variant="outline" className={STATUS_BG[inc.status]}>
                  {inc.status}
                </Badge>
                <Link href={`/incidents/${inc.id}`} className="tech-chip cursor-pointer text-accent-light hover:bg-accent/15" aria-label={`Open ${inc.id}`}>
                  Investigate <ArrowRight className="h-3 w-3" />
                </Link>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
