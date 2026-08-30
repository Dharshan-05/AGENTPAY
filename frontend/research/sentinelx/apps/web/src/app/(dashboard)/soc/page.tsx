"use client"

import { memo, useCallback, useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bot,
  Cpu,
  Database,
  Globe,
  ListTodo,
  Map,
  Radar,
  Search,
  Server,
  ShieldAlert,
  ShieldCheck,
  Siren,
  Wifi,
  Zap,
} from "lucide-react"
import { api, timeAgo } from "@/lib/api"
import type { SocStats } from "@/types"
import { Badge, DecisionBadge, PageHeader } from "@/components/ui/primitives"
import { Skeleton } from "@/components/ui/motion"
import { WorldThreatMap } from "@/components/ui/world-map"
import { LiveCursorLayer } from "@/components/ui/live-cursors"
import { RiskSimulator } from "@/components/ui/simulator"
import { PresencePanel } from "@/components/ui/presence"
import { cn } from "@/lib/utils"

const STATUS_TONE: Record<string, string> = {
  OPERATIONAL: "text-status-low",
  DEGRADED: "text-status-medium",
  DOWN: "text-status-critical",
}

const STATUS_ICON: Record<string, typeof Cpu> = {
  api: Server,
  agents: Bot,
  websocket: Wifi,
  queue: ListTodo,
  redis: Database,
  database: Database,
}

function ThroughputChart({ data, live }: { data: Array<{ t: number; pps: number }>; live: number }) {
  const W = 800
  const H = 72
  const max = Math.max(...data.map((d) => d.pps), 1)
  const step = W / (data.length - 1)
  const points = data.map((d, i) => `${i * step},${H - (d.pps / max) * (H - 8) - 4}`).join(" ")
  const lastIdx = live % data.length
  const liveX = lastIdx * step
  const liveY = H - (data[lastIdx].pps / max) * (H - 8) - 4

  return (
    <div className="relative overflow-hidden rounded-lg border border-border-default bg-bg-secondary/40">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Pipeline throughput over time">
        <defs>
          <linearGradient id="tpGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0ea79c" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#0ea79c" stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={`0,${H} ${points} ${W},${H}`} fill="url(#tpGrad)" />
        <motion.polyline
          points={points}
          fill="none"
          stroke="#0ea79c"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2 }}
        />
        <motion.circle
          key={liveX}
          cx={liveX}
          cy={liveY}
          r="4"
          fill="#0ea79c"
          initial={{ opacity: 0, r: 2 }}
          animate={{ opacity: [0.4, 1, 0.4], r: [3, 5, 3] }}
          transition={{ duration: 1.6, repeat: Infinity }}
        />
        <line x1={liveX} y1={0} x2={liveX} y2={H} stroke="rgba(14,167,156,0.25)" strokeWidth="1" strokeDasharray="3 3" />
      </svg>
    </div>
  )
}

export const MemoThroughput = memo(ThroughputChart)

export default function SocPage() {
  const [stats, setStats] = useState<SocStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [liveDot, setLiveDot] = useState(0)

  const load = useCallback(async () => {
    try {
      const d = await api.soc()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 10000)
    return () => clearInterval(t)
  }, [load])

  useEffect(() => {
    const t = setInterval(() => setLiveDot((v) => v + 1), 2200)
    return () => clearInterval(t)
  }, [])

  const maxStreamRisk = useMemo(() => Math.max(...(stats?.stream.map((s) => s.risk) ?? [0]), 1), [stats])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-56" />
            <Skeleton className="h-4 w-72" />
          </div>
        </div>
        <Skeleton className="h-64 rounded-xl" />
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Skeleton className="h-72 rounded-xl" />
          <Skeleton className="h-72 rounded-xl" />
          <Skeleton className="h-72 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <ShieldAlert className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">SOC telemetry unreachable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <Zap className="h-3 w-3" /> Retry
        </button>
      </div>
    )
  }

  const tick = stats.stream.length > 0 ? liveDot % stats.stream.length : 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Operations Center"
        description="Live mission control — global telemetry, incident queue, and agent orchestration in real time."
        actions={
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-low opacity-60" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-status-low" />
            </span>
            <Badge variant="success">LIVE</Badge>
            <span className="text-[11px] text-text-muted">{stats.totalIncidents} open incidents</span>
          </div>
        }
      />

      {/* Critical alert banner */}
      {stats.criticalAlert && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap items-center gap-4 rounded-xl border border-status-critical/30 bg-critical p-4"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-critical/20">
            <Siren className="h-5 w-5 text-status-critical animate-pulse" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-status-critical">{stats.criticalAlert.title}</p>
            <p className="truncate text-xs text-text-secondary">
              {stats.criticalAlert.department} · {stats.criticalAlert.risk}/100 · {stats.criticalAlert.prompt}
            </p>
          </div>
          <DecisionBadge decision={stats.criticalAlert.decision} />
          <Link
            href="/incidents"
            className="tech-chip cursor-pointer border-status-critical/40 text-status-critical transition-all hover:bg-status-critical/20"
          >
            Investigate <ArrowRight className="h-3 w-3" />
          </Link>
        </motion.div>
      )}

      {/* Threat ticker */}
      {stats.ticker.length > 0 && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="overflow-hidden rounded-xl border border-border-default bg-white/[0.02]">
          <div className="flex items-stretch">
            <span className="flex flex-shrink-0 items-center gap-1.5 border-r border-border-default bg-critical/20 px-3 text-[10px] font-semibold uppercase tracking-wider text-status-critical">
              <Siren className="h-3 w-3 animate-pulse" /> Live feed
            </span>
            <div className="relative flex-1 overflow-hidden">
              <div className="flex w-max animate-[ticker_28s_linear_infinite] items-center gap-8 px-4 py-2">
                {stats.ticker.map((t) => (
                  <span key={t.id} className="flex items-center gap-2 whitespace-nowrap text-[11px] text-text-secondary">
                    <span className={cn("h-1.5 w-1.5 flex-shrink-0 rounded-full", t.risk >= 80 ? "bg-status-critical" : t.risk >= 60 ? "bg-status-high" : "bg-status-low")} />
                    {t.text}
                    <DecisionBadge decision={t.decision} />
                  </span>
                ))}
                {stats.ticker.map((t) => (
                  <span key={`${t.id}-dup`} aria-hidden className="flex items-center gap-2 whitespace-nowrap text-[11px] text-text-secondary">
                    <span className={cn("h-1.5 w-1.5 flex-shrink-0 rounded-full", t.risk >= 80 ? "bg-status-critical" : t.risk >= 60 ? "bg-status-high" : "bg-status-low")} />
                    {t.text}
                    <DecisionBadge decision={t.decision} />
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* World threat map */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-6">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Globe className="h-4 w-4 text-accent-light" /> Global Threat Telemetry
          </h3>
          <div className="flex items-center gap-2 text-[11px] text-text-muted">
            <Map className="h-3.5 w-3.5" /> simulated · {stats.threatMap.length} live sources
          </div>
        </div>
        <div className="relative">
          <WorldThreatMap data={stats.threatMap} />
          <LiveCursorLayer className="absolute inset-0 z-10" />
        </div>
        <p className="mt-2 flex items-center gap-1.5 text-[10px] text-text-muted">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-status-low" /> 5 analysts collaborating in real time
        </p>
      </motion.div>

      {/* Live counters */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {[
          { label: "Threats", value: stats.counters.threats, icon: AlertTriangle, color: "text-status-critical" },
          { label: "AI Agents", value: stats.counters.agents, icon: Bot, color: "text-accent-light" },
          { label: "Avg latency", value: `${stats.counters.latency}ms`, icon: Zap, color: "text-status-info" },
          { label: "Blocked prompts", value: stats.counters.blockedPrompts, icon: ShieldCheck, color: "text-status-low" },
          { label: "Protected records", value: stats.counters.protectedRecords, icon: Database, color: "text-status-low" },
          { label: "Active attacks", value: stats.counters.activeAttacks, icon: Siren, color: "text-status-high" },
        ].map((c, i) => (
          <motion.div key={c.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="glass-card p-3.5">
            <div className="flex items-center gap-1.5">
              <c.icon className={cn("h-3.5 w-3.5", c.color)} />
              <p className="text-[10px] uppercase tracking-wider text-text-muted">{c.label}</p>
            </div>
            <p className="mono mt-1.5 text-xl font-semibold text-text-primary">{c.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Pipeline throughput */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.04 } }} className="glass-card card-glow p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Activity className="h-4 w-4 text-accent-light" /> Pipeline Throughput
          </h3>
          <div className="flex items-center gap-3 text-[10px] text-text-muted">
            <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-accent-light pulse-dot" /> prompts / min</span>
            <span className="mono text-accent-light">
              {Math.round(stats.throughput.reduce((a, p) => a + p.pps, 0) / stats.throughput.length)} avg
            </span>
          </div>
        </div>
        <MemoThroughput data={stats.throughput} live={liveDot} />
      </motion.div>

      {/* Global Threat Feed */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Globe className="h-4 w-4 text-status-critical" /> Global Threat Feed
          </h3>
          <div className="flex items-center gap-3 text-[10px] text-text-muted">
            <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-status-critical pulse-dot" />pulse</span>
            <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-status-high pulse-dot" />routing</span>
            <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-status-medium pulse-dot" />containment</span>
            <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-status-low" />resolved</span>
          </div>
        </div>
        <div className="grid gap-3 lg:grid-cols-2">
          {stats.regions.map((r, i) => {
            const phaseColor =
              r.phase === "PULSE" ? "bg-status-critical" : r.phase === "ROUTING" ? "bg-status-high" : r.phase === "CONTAINING" ? "bg-status-medium" : "bg-status-low"
            const phaseText =
              r.phase === "PULSE" ? "text-status-critical" : r.phase === "ROUTING" ? "text-status-high" : r.phase === "CONTAINING" ? "text-status-medium" : "text-status-low"
            const total = Math.max(r.attacks, 1)
            return (
              <motion.div key={r.city} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }} className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className={cn("relative flex h-2.5 w-2.5", r.phase !== "RESOLVED" && "pulse-dot")}>
                      <span className={cn("absolute inline-flex h-full w-full rounded-full opacity-60", phaseColor, r.phase !== "RESOLVED" && "animate-ping")} />
                      <span className={cn("relative inline-flex h-2.5 w-2.5 rounded-full", phaseColor)} />
                    </span>
                    <span className="text-sm font-semibold text-text-primary">{r.city}</span>
                    <span className="tech-chip">{r.code}</span>
                    <span className={cn("text-[10px] font-semibold uppercase tracking-wider", phaseText)}>{r.phase}</span>
                  </div>
                  <span className="mono text-[10px] text-text-muted">last seen {r.lastSeen}</span>
                </div>
                <div className="mt-3 flex items-center gap-2 text-[11px] text-text-muted">
                  <span className="mono text-text-primary">{r.attacks}</span> attacks
                  <span className="mx-1 text-text-muted/30">·</span>
                  <span className="mono text-status-critical">{r.active}</span> active
                  <span className="mx-1 text-text-muted/30">·</span>
                  <span className="mono text-status-medium">{r.containing}</span> containing
                  <span className="mx-1 text-text-muted/30">·</span>
                  <span className="mono text-status-low">{r.resolved}</span> resolved
                </div>
                <div className="mt-2 flex h-1.5 gap-1 overflow-hidden rounded-full">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(r.active / total) * 100}%` }}
                    transition={{ duration: 0.7, delay: i * 0.05 }}
                    className="h-full rounded-full bg-status-critical"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(r.containing / total) * 100}%` }}
                    transition={{ duration: 0.7, delay: i * 0.08 }}
                    className="h-full rounded-full bg-status-medium"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(r.resolved / total) * 100}%` }}
                    transition={{ duration: 0.7, delay: i * 0.11 }}
                    className="h-full rounded-full bg-status-low"
                  />
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* Agent activity + incident queue + presence */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Agent activity graph */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Radar className="h-4 w-4 text-accent-light" /> AI Agent Activity
          </h3>
          <div className="space-y-2.5">
            {stats.agentActivity.map((a, i) => {
              const total = Math.max(a.active + a.idle, 1)
              const pct = Math.round((a.active / total) * 100)
              return (
                <motion.div key={a.agent} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-3">
                  <span className="w-32 truncate text-[11px] text-text-secondary">{a.agent}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.8, delay: i * 0.05 }}
                      className="h-full rounded-full bg-gradient-to-r from-accent-dark to-accent-light"
                    />
                  </div>
                  <span className="mono w-7 text-right text-[10px] text-text-muted">{pct}%</span>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Incident queue */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <AlertTriangle className="h-4 w-4 text-status-critical" /> Incident Queue
            </h3>
            <Badge variant="danger">{stats.incidentQueue.length}</Badge>
          </div>
          <div className="space-y-2">
            {stats.incidentQueue.map((inc, i) => (
              <motion.div
                key={inc.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-2.5"
              >
                <span
                  className={cn(
                    "h-2 w-2 flex-shrink-0 rounded-full",
                    inc.risk >= 80 ? "bg-status-critical" : inc.risk >= 60 ? "bg-status-high" : inc.risk >= 35 ? "bg-status-medium" : "bg-status-low",
                  )}
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-medium text-text-primary">{inc.title}</p>
                  <p className="text-[10px] text-text-muted">{inc.id} · {inc.department} · {inc.age}m</p>
                </div>
                <span className={cn("text-[10px] font-semibold uppercase tracking-wider", inc.status === "ACTIVE" ? "text-status-critical" : "text-text-muted")}>
                  {inc.status}
                </span>
              </motion.div>
            ))}
            {stats.incidentQueue.length === 0 && <p className="py-6 text-center text-xs text-text-muted">No open incidents</p>}
          </div>
        </motion.div>

        {/* Processing queue + investigations */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="space-y-4">
          <div className="glass-card card-glow p-5">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <ListTodo className="h-4 w-4 text-accent-light" /> Processing Queue
            </h3>
            <div className="space-y-2">
              {stats.processingQueue.map((p, i) => (
                <motion.div key={p.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="rounded-lg border border-border-default bg-white/[0.02] p-2.5">
                  <div className="flex items-center justify-between">
                    <span className="mono text-[10px] text-text-muted">{p.id}</span>
                    <span className="text-[10px] text-accent-light">{p.stage}</span>
                  </div>
                  <p className="mt-1 truncate text-[11px] text-text-secondary">{p.prompt}</p>
                  <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${p.pct}%` }} transition={{ duration: 0.6, delay: i * 0.05 }} className="h-full rounded-full bg-accent" />
                  </div>
                </motion.div>
              ))}
            </div>
            {stats.processingQueue.length === 0 && (
              <p className="rounded-lg border border-dashed border-border-default px-3 py-4 text-center text-xs text-text-muted">
                Queue empty — no prompts in flight
              </p>
            )}
          </div>

          <div className="glass-card card-glow p-5">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Search className="h-4 w-4 text-accent-light" /> Current Investigations
            </h3>
            <div className="space-y-2">
              {stats.investigations.map((inv, i) => (
                <motion.div key={inv.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-3">
                  <span className="mono text-[10px] text-text-muted">{inv.id}</span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[11px] font-medium text-text-primary">{inv.title}</p>
                    <p className="text-[10px] text-text-muted">{inv.assignee}</p>
                  </div>
                  <div className="w-16">
                    <div className="h-1 overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div initial={{ width: 0 }} animate={{ width: `${inv.progress}%` }} transition={{ duration: 0.6, delay: i * 0.05 }} className="h-full rounded-full bg-status-info" />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            {stats.investigations.length === 0 && (
              <p className="rounded-lg border border-dashed border-border-default px-3 py-4 text-center text-xs text-text-muted">
                No open investigations
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Live attack stream */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }} className="glass-card card-glow p-6">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Activity className="h-4 w-4 text-status-critical" /> Live Attack Stream
          </h3>
          <Badge variant="info">streaming</Badge>
        </div>
        <div className="space-y-1.5">
          <AnimatePresence initial={false}>
            {stats.stream.slice(0, 12).map((s) => {
              const isLive = s.ts === tick
              return (
                <motion.div
                  key={s.id}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: isLive ? 1 : 0.55, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className={cn("flex items-center gap-3 rounded-lg px-2 py-1.5", isLive && "bg-accent/[0.06]")}
                >
                  <span className="mono w-14 text-[10px] text-text-muted">{timeAgo(s.timestamp)}</span>
                  <div className="h-1.5 w-24 flex-shrink-0 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${(s.risk / maxStreamRisk) * 100}%` }} transition={{ duration: 0.5 }} className={cn("h-full rounded-full", s.risk >= 80 ? "bg-status-critical" : s.risk >= 60 ? "bg-status-high" : s.risk >= 35 ? "bg-status-medium" : "bg-status-low")} />
                  </div>
                  <span className="mono w-8 text-[10px] text-text-muted">{s.risk}</span>
                  <span className="w-32 truncate text-[11px] text-text-secondary">{s.user} · {s.department}</span>
                  <span className="hidden min-w-0 flex-1 truncate text-[11px] text-text-muted md:block">{s.prompt}</span>
                  <DecisionBadge decision={s.action} />
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
        {stats.stream.length === 0 && (
          <p className="rounded-lg border border-dashed border-border-default px-3 py-4 text-center text-xs text-text-muted">
            No events in stream yet — scans will appear here live
          </p>
        )}
      </motion.div>

      {/* Risk simulator + presence */}
      <div className="grid gap-4 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }}>
          <RiskSimulator />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }}>
          <PresencePanel />
        </motion.div>
      </div>

      {/* System health strip */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {Object.entries(stats.systemHealth).map(([key, item], i) => {
          const Icon = STATUS_ICON[key] ?? Cpu
          return (
            <motion.div key={key} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.05 }} className="glass-card p-3.5">
              <div className="flex items-center justify-between">
                <Icon className="h-3.5 w-3.5 text-text-muted" />
                <span className={cn("flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider", STATUS_TONE[item.status] ?? "text-text-muted")}>
                  <span className="h-1.5 w-1.5 rounded-full bg-current pulse-dot" />
                  {item.status}
                </span>
              </div>
              <p className="mt-2 text-[11px] font-medium text-text-primary">{item.label}</p>
              <p className="mono text-[10px] text-text-muted">{item.value ?? item.latency}</p>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
