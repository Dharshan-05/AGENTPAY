"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Building2,
  CheckCircle2,
  GitBranch,
  Lightbulb,
  Minus,
  Plus,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react"
import { api } from "@/lib/api"
import type { TwinDepartment, TwinStats } from "@/types"
import { Badge, PageHeader } from "@/components/ui/primitives"
import { Skeleton, CountUp } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const LEVEL_TONE: Record<string, string> = {
  HIGH: "text-status-critical",
  MEDIUM: "text-status-medium",
  LOW: "text-status-low",
  SAFE: "text-status-low",
}

function OrgGraph({
  departments,
  selected,
  onSelect,
}: {
  departments: TwinDepartment[]
  selected: string | null
  onSelect: (name: string) => void
}) {
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const dragRef = useRef<{ startX: number; startY: number; panX: number; panY: number; dragging: boolean }>({ startX: 0, startY: 0, panX: 0, panY: 0, dragging: false })
  const W = 760
  const H = 420
  const cx = W / 2
  const cy = H / 2
  const R = Math.min(W, H) * 0.32

  const nodes = departments.map((d, i) => {
    const angle = (i / departments.length) * Math.PI * 2 - Math.PI / 2
    return { ...d, x: cx + Math.cos(angle) * R, y: cy + Math.sin(angle) * R }
  })

  const onPointerDown = (e: React.PointerEvent) => {
    dragRef.current = { startX: e.clientX, startY: e.clientY, panX: pan.x, panY: pan.y, dragging: true }
    ;(e.target as Element).setPointerCapture?.(e.pointerId)
  }
  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragRef.current.dragging) return
    setPan({ x: dragRef.current.panX + (e.clientX - dragRef.current.startX), y: dragRef.current.panY + (e.clientY - dragRef.current.startY) })
  }
  const onPointerUp = () => {
    dragRef.current.dragging = false
  }

  return (
    <div className="glass-card card-glow p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <Building2 className="h-4 w-4 text-accent-light" /> Organization Risk Graph
        </h3>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-text-muted">drag to pan · scroll or +/− to zoom</span>
          <button onClick={() => setZoom((z) => Math.min(2.2, z + 0.25))} aria-label="Zoom in" className="rounded-md border border-border-default bg-white/[0.02] p-1.5 text-text-secondary transition-colors hover:border-accent/50 hover:text-accent-light">
            <Plus className="h-3.5 w-3.5" />
          </button>
          <button onClick={() => setZoom((z) => Math.max(0.6, z - 0.25))} aria-label="Zoom out" className="rounded-md border border-border-default bg-white/[0.02] p-1.5 text-text-secondary transition-colors hover:border-accent/50 hover:text-accent-light">
            <Minus className="h-3.5 w-3.5" />
          </button>
          <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }) }} className="rounded-md border border-border-default bg-white/[0.02] px-2 py-1.5 text-[10px] text-text-secondary transition-colors hover:border-accent/50 hover:text-accent-light">
            reset
          </button>
        </div>
      </div>
      <div
        className="relative touch-none select-none overflow-hidden rounded-xl border border-border-default bg-bg-secondary/40"
        style={{ height: H }}
        onWheel={(e) => setZoom((z) => Math.min(2.2, Math.max(0.6, z - e.deltaY * 0.0015)))}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <div className="absolute inset-0 origin-center transition-transform duration-75" style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }}>
          <svg viewBox={`0 0 ${W} ${H}`} className="mx-auto block h-auto w-full max-w-[760px]">
            <defs>
              <radialGradient id="orgGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#0b827a" stopOpacity={0.12} />
                <stop offset="100%" stopColor="#0b827a" stopOpacity={0} />
              </radialGradient>
            </defs>
            <circle cx={cx} cy={cy} r={R + 40} fill="url(#orgGlow)" />
            {nodes.map((n, i) => {
              const next = nodes[(i + 1) % nodes.length]
              const active = selected === n.name || selected === next.name
              return (
                <motion.line
                  key={`edge-${i}`}
                  x1={n.x} y1={n.y} x2={next.x} y2={next.y}
                  stroke={active ? n.color : "rgba(11,130,122,0.25)"}
                  strokeWidth={active ? 2 : 1}
                  strokeDasharray={active ? "6 4" : "0"}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: active ? 0.9 : 0.45 }}
                  transition={{ duration: 1.2, delay: i * 0.1 }}
                />
              )
            })}
            {nodes.map((n, i) => {
              const isSel = selected === n.name
              return (
                <motion.g
                  key={n.name}
                  initial={{ opacity: 0, scale: 0.6 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.08, type: "spring", stiffness: 260, damping: 20 }}
                  role="button"
                  tabIndex={0}
                  aria-pressed={isSel}
                  aria-label={`Select ${n.name} department`}
                  style={{ cursor: "pointer" }}
                  onClick={() => onSelect(n.name)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault()
                      onSelect(n.name)
                    }
                  }}
                >
                  <circle cx={n.x} cy={n.y} r={isSel ? 30 : 26} fill={`${n.color}18`} stroke={isSel ? n.color : `${n.color}66`} strokeWidth={isSel ? 2.5 : 1.5} />
                  {n.riskIndex >= 60 && (
                    <circle cx={n.x} cy={n.y} r={30} fill="none" stroke={n.color} strokeWidth={1}>
                      <animate attributeName="r" values="28;38;28" dur="2s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.8;0.1;0.8" dur="2s" repeatCount="indefinite" />
                    </circle>
                  )}
                  <text x={n.x} y={n.y - 4} textAnchor="middle" fill="#fafafa" fontSize="11" fontWeight="600">{n.name}</text>
                  <text x={n.x} y={n.y + 14} textAnchor="middle" fill="#a1a1aa" fontSize="9">{n.riskIndex}% risk</text>
                  <text x={n.x} y={n.y + 27} textAnchor="middle" fill={n.color} fontSize="9" fontWeight="700">{n.riskLevel}</text>
                </motion.g>
              )
            })}
          </svg>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {nodes.map((n) => (
          <span key={n.name} className="flex items-center gap-1.5 rounded-full border border-border-default bg-white/[0.02] px-2.5 py-1 text-[10px] text-text-secondary">
            <span className="h-2 w-2 rounded-full" style={{ background: n.color }} />
            {n.name}
            <span className="mono text-text-muted">{n.people}</span>
          </span>
        ))}
      </div>
    </div>
  )
}

function DepartmentCard({ dept, selected, onSelect }: { dept: TwinDepartment; selected: boolean; onSelect: () => void }) {
  return (
    <motion.button
      onClick={onSelect}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className={cn(
        "relative overflow-hidden rounded-xl border p-5 text-left transition-all duration-200",
        selected ? "border-accent/50 bg-accent/[0.06] shadow-glow" : "border-border-default bg-white/[0.02] hover:border-border-strong",
      )}
      aria-pressed={selected}
    >
      <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full opacity-10" style={{ background: dept.color }} />
      <div className="flex items-start justify-between">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ background: `${dept.color}22`, color: dept.color }}>
          <Users className="h-5 w-5" />
        </span>
        <Badge variant={dept.riskLevel === "HIGH" ? "danger" : dept.riskLevel === "MEDIUM" ? "warning" : "success"}>{dept.riskLevel}</Badge>
      </div>
      <p className="mt-3 text-sm font-semibold text-text-primary">{dept.name}</p>
      <p className="text-[11px] text-text-muted">{dept.people} employees · {dept.policies} policies</p>
      <div className="mt-3">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-text-muted">Risk index</span>
          <span className={cn("mono font-semibold", LEVEL_TONE[dept.riskLevel])}>{dept.riskIndex}%</span>
        </div>
        <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${dept.riskIndex}%` }}
            transition={{ duration: 0.8 }}
            className={cn("h-full rounded-full", dept.riskIndex >= 70 ? "bg-status-critical" : dept.riskIndex >= 40 ? "bg-status-medium" : dept.riskIndex >= 15 ? "bg-status-low" : "bg-status-low")}
          />
        </div>
      </div>
    </motion.button>
  )
}

export default function TwinPage() {
  const [stats, setStats] = useState<TwinStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<TwinDepartment | null>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.twin()
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

  useEffect(() => {
    if (stats?.departments && !selected) setSelected(stats.departments[0] ?? null)
  }, [stats, selected])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-4 w-72" />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (!stats || stats.departments.length === 0) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <Building2 className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">Organization twin unreachable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <Zap className="h-3 w-3" /> Retry
        </button>
      </div>
    )
  }

  const avgRisk = Math.round(stats.departments.reduce((a, d) => a + d.riskIndex, 0) / stats.departments.length)
  const totalViolations = stats.departments.reduce((a, d) => a + d.violations, 0)
  const totalIncidents = stats.departments.reduce((a, d) => a + d.incidents, 0)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Organization Digital Twin"
        description="An interactive mirror of every department's AI risk posture — click any team to inspect its security DNA."
        actions={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[11px] text-text-muted">
              <TrendingUp className="h-3.5 w-3.5 text-status-medium" /> avg risk {avgRisk}%
            </div>
            <Badge variant="info">simulated</Badge>
          </div>
        }
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Departments", value: stats.departments.length, icon: Building2, tone: "text-accent-light" },
          { label: "Avg Risk Index", value: avgRisk, suffix: "%", icon: ShieldAlert, tone: avgRisk >= 40 ? "text-status-medium" : "text-status-low" },
          { label: "Policy Violations", value: totalViolations, icon: ShieldAlert, tone: "text-status-high" },
          { label: "Open Incidents", value: totalIncidents, icon: Zap, tone: "text-status-critical" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card card-glow p-4">
            <s.icon className={cn("h-4 w-4", s.tone)} />
            <p className="mt-2 text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
            <p className={cn("mono mt-1 text-2xl font-semibold", s.tone)}>
              <CountUp value={s.value} suffix={s.suffix ?? ""} />
            </p>
          </motion.div>
        ))}
      </div>

      {/* Organization graph */}
      <OrgGraph departments={stats.departments} selected={selected?.name ?? null} onSelect={(name) => setSelected(stats.departments.find((d) => d.name === name) ?? null)} />

      {/* Department grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.departments.map((dept) => (
          <DepartmentCard key={dept.name} dept={dept} selected={selected?.name === dept.name} onSelect={() => setSelected(dept)} />
        ))}
      </div>

      {/* Detail panel */}
      <AnimatePresence mode="wait">
        {selected && (
          <motion.div
            key={selected.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="glass-card card-glow p-6"
          >
            <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-center gap-4">
                <span className="flex h-12 w-12 items-center justify-center rounded-xl" style={{ background: `${selected.color}22`, color: selected.color }}>
                  <Building2 className="h-6 w-6" />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold text-text-primary">{selected.name}</h2>
                    <Badge variant={selected.riskLevel === "HIGH" ? "danger" : selected.riskLevel === "MEDIUM" ? "warning" : "success"}>{selected.riskLevel} RISK</Badge>
                  </div>
                  <p className="mt-0.5 text-xs text-text-muted">
                    {selected.people} employees · {selected.policies} policies · {selected.totalPrompts} prompts audited · {selected.avgScore} avg risk
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="tech-chip"><TrendingDown className="h-3 w-3 text-status-low" /> risk index</span>
                <span className={cn("mono text-2xl font-bold", LEVEL_TONE[selected.riskLevel])}>{selected.riskIndex}%</span>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              {/* Recent incidents */}
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <ShieldAlert className="h-4 w-4 text-status-critical" /> Recent Incidents
                </h3>
                <div className="space-y-2">
                  {selected.recentIncidents.map((inc) => (
                    <div key={inc.id} className="flex items-center justify-between rounded-lg bg-white/[0.02] px-3 py-2">
                      <div className="min-w-0">
                        <p className="truncate text-[11px] font-medium text-text-primary">{inc.title}</p>
                        <p className="text-[10px] text-text-muted">{inc.time}</p>
                      </div>
                      <span className={cn("mono text-[11px] font-semibold", inc.risk >= 80 ? "text-status-critical" : "text-status-high")}>{inc.risk}</span>
                    </div>
                  ))}
                  {selected.recentIncidents.length === 0 && <p className="py-4 text-center text-xs text-text-muted">No recent incidents</p>}
                </div>
              </div>

              {/* Common violations */}
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <Shield className="h-4 w-4 text-status-high" /> Common Violations
                </h3>
                <div className="space-y-2">
                  {selected.commonViolations.map((v, i) => (
                    <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-center gap-2 rounded-lg bg-white/[0.02] px-3 py-2">
                      <GitBranch className="h-3 w-3 flex-shrink-0 text-status-medium" />
                      <span className="text-[11px] text-text-secondary">{v}</span>
                    </motion.div>
                  ))}
                  {selected.commonViolations.length === 0 && <p className="py-4 text-center text-xs text-text-muted">No violations</p>}
                </div>
                <div className="mt-4 rounded-xl border border-accent/20 bg-accent/[0.04] p-3">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-text-secondary">Policy compliance</span>
                    <span className="mono font-semibold text-accent-light">{selected.complianceScore}%</span>
                  </div>
                  <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${selected.complianceScore}%` }} transition={{ duration: 0.8 }} className="h-full rounded-full bg-gradient-to-r from-accent-dark to-accent-light" />
                  </div>
                </div>
              </div>

              {/* Suggested improvements */}
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <Lightbulb className="h-4 w-4 text-accent-light" /> Suggested Improvements
                </h3>
                <div className="space-y-2">
                  {selected.improvements.map((imp, i) => (
                    <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="flex items-start gap-2 rounded-lg bg-white/[0.02] px-3 py-2">
                      <Sparkles className="mt-0.5 h-3 w-3 flex-shrink-0 text-accent-light" />
                      <span className="text-[11px] leading-relaxed text-text-secondary">{imp}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            {/* Enforced policies */}
            {selected.policyNames && selected.policyNames.length > 0 && (
              <div className="mt-4 rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-2.5 flex items-center gap-2 text-xs font-semibold">
                  <ShieldCheck className="h-3.5 w-3.5 text-accent-light" /> Enforced Policies
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {selected.policyNames.map((p) => (
                    <span key={p} className="rounded bg-accent/10 px-2 py-1 text-[10px] text-accent-light">{p}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Compliance breakdown row */}
            <div className="mt-4 grid gap-3 sm:grid-cols-5">
              {[
                { label: "GDPR", v: Math.max(50, selected.complianceScore - 6) },
                { label: "HIPAA", v: Math.max(50, selected.complianceScore - 2) },
                { label: "PCI DSS", v: Math.max(50, selected.complianceScore - 8) },
                { label: "SOC 2", v: Math.max(50, selected.complianceScore - 3) },
                { label: "ISO 27001", v: Math.max(50, selected.complianceScore - 4) },
              ].map((c) => (
                <div key={c.label} className="rounded-lg bg-white/[0.02] p-2.5 text-center">
                  <p className="text-[10px] text-text-muted">{c.label}</p>
                  <p className="mono text-sm font-semibold text-status-low">{c.v}%</p>
                  <CheckCircle2 className="mx-auto mt-1 h-3 w-3 text-status-low" />
                </div>
              ))}
            </div>

            {/* Risk trend + regulation heatmap + users */}
            <div className="mt-4 grid gap-4 lg:grid-cols-3">
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold">
                  <TrendingUp className="h-3.5 w-3.5 text-status-medium" /> Risk Trend · 7 days
                </h3>
                <DepartmentTrend data={selected.trend} color={selected.color} />
              </div>
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-3 flex items-center gap-2 text-xs font-semibold">
                  <ShieldCheck className="h-3.5 w-3.5 text-accent-light" /> Regulation Heatmap
                </h3>
                <div className="space-y-2">
                  {selected.heatmap.map((h) => (
                    <div key={h.regulation} className="flex items-center gap-2.5">
                      <span className="w-16 text-[10px] text-text-muted">{h.regulation}</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${h.score}%` }}
                          transition={{ duration: 0.7 }}
                          className="h-full rounded-full"
                          style={{ background: h.score >= 90 ? "#22c55e" : h.score >= 75 ? "#eab308" : "#f97316" }}
                        />
                      </div>
                      <span className="mono w-9 text-right text-[10px] text-text-secondary">{h.score}%</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
                <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold">
                  <Users className="h-3.5 w-3.5 text-status-info" /> Department Users
                </h3>
                <div className="space-y-1.5">
                  {selected.users.map((u, i) => (
                    <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }} className="flex items-center justify-between rounded-lg bg-white/[0.02] px-2.5 py-1.5">
                      <span className="truncate text-[10px] text-text-secondary">{u.name}</span>
                      <div className="flex items-center gap-2">
                        <span className={cn("mono text-[9px]", u.risky > 0 ? "text-status-high" : "text-text-muted")}>{u.prompts} prompts</span>
                        <span className={cn("mono rounded px-1.5 text-[8px]", u.score >= 60 ? "bg-status-critical/10 text-status-critical" : u.score >= 30 ? "bg-medium/10 text-status-medium" : "bg-low/10 text-status-low")}>
                          risk {u.score}
                        </span>
                        {u.risky > 0 && <span className="mono rounded bg-status-critical/10 px-1.5 text-[8px] text-status-critical">{u.risky} risky</span>}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function DepartmentTrend({ data, color }: { data: Array<{ day: string; score: number }>; color: string }) {
  const max = Math.max(...data.map((d) => d.score), 1)
  const W = 300
  const H = 70
  const step = W / Math.max(data.length - 1, 1)
  const points = data.map((d, i) => `${i * step},${H - (d.score / max) * (H - 8) - 4}`).join(" ")
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Department risk trend">
        <defs>
          <linearGradient id="deptTrendGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={`0,${H} ${points} ${W},${H}`} fill="url(#deptTrendGrad)" />
        <motion.polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1 }} />
      </svg>
      <div className="mt-1 flex justify-between text-[8px] text-text-muted">
        {data.map((d) => (
          <span key={d.day}>{d.day}</span>
        ))}
      </div>
    </div>
  )
}
