"use client"

import { useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import {
  Activity,
  Boxes,
  CheckCircle2,
  Cpu,
  Database,
  GitBranch,
  Globe,
  HardDrive,
  HeartPulse,
  Layers,
  MemoryStick,
  Radio,
  Server,
  ShieldCheck,
  Timer,
  Wifi,
  Zap,
} from "lucide-react"
import { api } from "@/lib/api"
import type { SystemStats } from "@/types"
import { Badge, PageHeader } from "@/components/ui/primitives"
import { Skeleton } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

function uptime(seconds: number): string {
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${d}d ${h}h ${m}m`
}

const INFRA_ROWS = [
  { key: "websocket" as const, label: "WebSocket Bridge", icon: Wifi },
  { key: "redis" as const, label: "Redis Cache", icon: Database },
  { key: "database" as const, label: "PostgreSQL", icon: Database },
  { key: "threatFeed" as const, label: "Threat Feed", icon: Radio },
]

export default function SystemPage() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const d = await api.system()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [load])

  const cpuPct = stats?.cpuPct ?? 0
  const memPct = stats ? Math.round((stats.memoryMb / stats.memoryTotalMb) * 100) : 0

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-56" />
            <Skeleton className="h-4 w-72" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-72 rounded-xl" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <Server className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">System telemetry unreachable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <Zap className="h-3 w-3" /> Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="System & Infrastructure"
        description="Deployment health, cluster state, and runtime telemetry for the SentinelX enterprise platform."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="success">all systems operational</Badge>
          </div>
        }
      />

      {/* Deployment info */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Version", value: stats.version, sub: stats.build, icon: GitBranch, tone: "text-accent-light" },
          { label: "Deployment", value: stats.deployment, sub: stats.region, icon: Globe, tone: "text-status-low" },
          { label: "Uptime", value: uptime(stats.uptimeSeconds), sub: "since last deploy", icon: Timer, tone: "text-status-info" },
          { label: "Cluster", value: stats.cluster.status, sub: `${stats.cluster.nodes} nodes · ${stats.cluster.drift} drift`, icon: Boxes, tone: "text-status-low" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card card-glow p-4">
            <div className="flex items-center justify-between">
              <s.icon className={cn("h-4 w-4", s.tone)} />
              <span className="text-[9px] uppercase tracking-wider text-text-muted">{s.label}</span>
            </div>
            <p className={cn("mono mt-2 text-lg font-semibold", s.tone)}>{s.value}</p>
            <p className="truncate text-[10px] text-text-muted">{s.sub}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Resource gauges */}
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <MemoryStick className="h-4 w-4 text-accent-light" /> Runtime Resources
          </h3>
          <div className="space-y-5">
            <div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-text-secondary"><Cpu className="h-3.5 w-3.5" /> CPU utilisation</span>
                <span className="mono text-text-primary">{cpuPct}%</span>
              </div>
              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${cpuPct}%` }}
                  transition={{ duration: 0.8 }}
                  className={cn("h-full rounded-full", cpuPct > 80 ? "bg-status-critical" : cpuPct > 60 ? "bg-status-medium" : "bg-gradient-to-r from-accent-dark to-accent-light")}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-text-secondary"><MemoryStick className="h-3.5 w-3.5" /> Memory</span>
                <span className="mono text-text-primary">{stats.memoryMb} MB / {stats.memoryTotalMb} MB</span>
              </div>
              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${memPct}%` }}
                  transition={{ duration: 0.8 }}
                  className={cn("h-full rounded-full", memPct > 80 ? "bg-status-critical" : memPct > 60 ? "bg-status-medium" : "bg-gradient-to-r from-accent-dark to-accent-light")}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-text-secondary"><Timer className="h-3.5 w-3.5" /> API latency</span>
                <span className="mono text-text-primary">{stats.apiLatency}ms</span>
              </div>
              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(100, stats.apiLatency * 2)}%` }} transition={{ duration: 0.8 }} className="h-full rounded-full bg-gradient-to-r from-accent-dark to-accent-light" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-text-secondary"><Activity className="h-3.5 w-3.5" /> Queue depth</span>
                <span className="mono text-text-primary">{stats.queueDepth} jobs</span>
              </div>
              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(100, stats.queueDepth * 15)}%` }} transition={{ duration: 0.8 }} className="h-full rounded-full bg-status-low" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Infrastructure status */}
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Layers className="h-4 w-4 text-accent-light" /> Infrastructure Status
          </h3>
          <div className="space-y-2.5">
            {INFRA_ROWS.map((row, i) => (
              <motion.div key={row.key} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-3">
                <row.icon className="h-4 w-4 text-text-muted" />
                <span className="flex-1 text-xs font-medium text-text-primary">{row.label}</span>
                <span className={cn("flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider", stats[row.key] === "connected" || stats[row.key] === "active" || stats[row.key] === "replicated" ? "text-status-low" : "text-status-critical")}>
                  <HeartPulse className="h-3 w-3" />
                  {stats[row.key]}
                </span>
              </motion.div>
            ))}
            <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-3">
              <Server className="h-4 w-4 text-text-muted" />
              <span className="flex-1 text-xs font-medium text-text-primary">Orchestration</span>
              <span className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-status-low">
                <CheckCircle2 className="h-3 w-3" /> {stats.podsHealthy}
              </span>
            </motion.div>
          </div>
        </motion.div>

        {/* Pods / replicas */}
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="glass-card card-glow p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Boxes className="h-4 w-4 text-accent-light" /> Compute Fleet
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "Pods", value: stats.pods, icon: Boxes },
              { label: "Replicas", value: stats.replicas, icon: Server },
              { label: "Healthy", value: stats.podsHealthy, icon: ShieldCheck },
              { label: "Canary", value: stats.canary, icon: GitBranch },
            ].map((c, i) => (
              <motion.div key={c.label} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.15 + i * 0.05 }} className="rounded-lg border border-border-default bg-white/[0.02] p-3 text-center">
                <c.icon className="mx-auto h-4 w-4 text-accent-light" />
                <p className="mono mt-2 text-xl font-semibold text-text-primary">{c.value}</p>
                <p className="text-[10px] uppercase tracking-wider text-text-muted">{c.label}</p>
              </motion.div>
            ))}
          </div>
          <div className="mt-4 rounded-xl border border-status-low/20 bg-low p-3">
            <p className="flex items-center gap-2 text-[11px] text-status-low">
              <ShieldCheck className="h-3.5 w-3.5" />
              Health check passing · zero drift · auto-scaling engaged
            </p>
          </div>
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-border-default bg-white/[0.02] p-3">
            <HardDrive className="h-4 w-4 text-text-muted" />
            <span className="flex-1 text-[11px] text-text-secondary">Persistent storage</span>
            <span className="mono text-[10px] text-status-low">encrypted · replicated</span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
