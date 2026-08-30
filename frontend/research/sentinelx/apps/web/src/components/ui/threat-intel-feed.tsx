"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { AlertTriangle, Crosshair, Eye, Globe2, Radar, ShieldAlert, ShieldCheck, Sparkles } from "lucide-react"
import { api } from "@/lib/api"
import type { ThreatAdvisory } from "@/types"
import { Badge } from "./primitives"
import { cn } from "@/lib/utils"

const SOURCE_ICON: Record<string, typeof Globe2> = {
  CISA: ShieldAlert,
  MITRE: Crosshair,
  OWASP: ShieldCheck,
  GitHub: Radar,
  OpenAI: Sparkles,
  Microsoft: Eye,
}

const SOURCE_COLOR: Record<string, string> = {
  CISA: "text-status-critical",
  MITRE: "text-status-high",
  OWASP: "text-status-medium",
  GitHub: "text-status-info",
  OpenAI: "text-accent-light",
  Microsoft: "text-status-low",
}

const CVSS_TONE = (v: number) => (v >= 9 ? "text-status-critical" : v >= 7 ? "text-status-high" : v >= 4 ? "text-status-medium" : "text-status-low")

export function ThreatIntelFeed() {
  const [feed, setFeed] = useState<ThreatAdvisory[] | null>(null)
  const [stats, setStats] = useState<{ total: number; active: number; critical: number; avgCvss: number } | null>(null)
  const [source, setSource] = useState<string | null>(null)
  const [lastSynced, setLastSynced] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.threatIntel()
      setFeed(d.feed)
      setStats(d.stats)
      setLastSynced(d.lastSynced)
    } catch {
      setFeed([])
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 60000)
    return () => clearInterval(t)
  }, [load])

  const rows = feed?.filter((a) => !source || a.source === source) ?? []

  return (
    <div className="glass-card card-glow p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Radar className="h-4 w-4 text-status-critical" />
          <h2 className="text-sm font-semibold">Threat Intelligence Feed</h2>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {["ALL", "CISA", "MITRE", "OWASP", "GitHub", "OpenAI", "Microsoft"].map((s) => (
            <button
              key={s}
              onClick={() => setSource(s === "ALL" ? null : s)}
              className={cn(
                "tech-chip cursor-pointer",
                source === s || (s === "ALL" && !source) ? "border-accent/50 bg-accent/10 text-accent-light" : "",
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { label: "Advisories", value: stats?.total ?? 0, tone: "text-text-primary" },
          { label: "Active threats", value: stats?.active ?? 0, tone: "text-status-critical" },
          { label: "Critical severity", value: stats?.critical ?? 0, tone: "text-status-high" },
          { label: "Avg CVSS", value: stats ? stats.avgCvss.toFixed(1) : "—", tone: "text-accent-light" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="rounded-lg border border-border-default bg-white/[0.02] p-3 text-center">
            <p className={cn("mono text-lg font-semibold", s.tone)}>{s.value}</p>
            <p className="text-[9px] uppercase tracking-wider text-text-muted">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {rows.map((a, i) => {
          const Icon = SOURCE_ICON[a.source] ?? Globe2
          return (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl border border-border-default bg-white/[0.02] p-4 transition-colors hover:border-border-strong"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className={cn("flex h-7 w-7 items-center justify-center rounded-lg bg-white/[0.04]", SOURCE_COLOR[a.source])}>
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">{a.title}</p>
                    <p className="text-[9px] uppercase tracking-wider text-text-muted">
                      {a.source} · {a.published}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={cn("mono text-sm font-bold", CVSS_TONE(a.cvss))}>CVSS {a.cvss.toFixed(1)}</span>
                  <Badge variant={a.status === "ACTIVE" ? "danger" : a.status === "WATCHING" ? "warning" : "success"}>{a.status}</Badge>
                </div>
              </div>

              <p className="mt-2.5 text-[11px] leading-relaxed text-text-muted">{a.description}</p>

              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                {a.cve && <span className="mono rounded bg-status-critical/10 px-2 py-0.5 text-[9px] text-status-critical">{a.cve}</span>}
                {a.tactic && <span className="tech-chip">{a.tactic}</span>}
                <span className="tech-chip">affected: {a.affected}</span>
              </div>

              <div className="mt-2.5 grid gap-1.5 sm:grid-cols-2">
                <div className="rounded-lg border border-border-subtle bg-white/[0.01] p-2.5">
                  <p className="text-[9px] uppercase tracking-wider text-accent-light">Mitigation</p>
                  <p className="mt-0.5 text-[10px] leading-relaxed text-text-secondary">{a.mitigation}</p>
                </div>
                <div className="rounded-lg border border-border-subtle bg-white/[0.01] p-2.5">
                  <p className="flex items-center gap-1 text-[9px] uppercase tracking-wider text-text-muted">
                    <AlertTriangle className="h-2.5 w-2.5" /> SentinelX relevance
                  </p>
                  <p className="mt-0.5 text-[10px] leading-relaxed text-text-secondary">{a.relevance}</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <p className="mt-4 flex items-center justify-between text-[9px] text-text-muted">
        <span>Correlated from authoritative sources · seeded dataset for demo</span>
        <span className="mono">last synced {lastSynced ? new Date(lastSynced).toLocaleTimeString() : "…"}</span>
      </p>
    </div>
  )
}
