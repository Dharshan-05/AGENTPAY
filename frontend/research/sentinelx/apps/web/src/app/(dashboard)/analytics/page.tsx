"use client"

import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react"
import { motion } from "framer-motion"
import {
  BarChart3,
  CalendarClock,
  Clock,
  Cpu,
  Download,
  Filter,
  Gauge,
  LineChart as LineChartIcon,
  PieChart as PieChartIcon,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Brush,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { api } from "@/lib/api"
import type { AnalyticsStats } from "@/types"
import { Badge, PageHeader } from "@/components/ui/primitives"
import { Skeleton } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const tooltipStyle = {
  background: "#1c1c21",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  fontSize: 12,
} as const

const PIE_COLORS = ["#0ea79c", "#3b82f6", "#eab308", "#f97316", "#a855f7", "#22c55e", "#ef4444", "#ec4899"]

function ChartCard({ title, icon: Icon, children, delay = 0, badge }: { title: string; icon: typeof BarChart3; children: React.ReactNode; delay?: number; badge?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card card-glow p-5"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <Icon className="h-4 w-4 text-accent-light" /> {title}
        </h3>
        {badge && <Badge variant="outline">{badge}</Badge>}
      </div>
      {children}
    </motion.div>
  )
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

export const MemoIncidentHeatmap = memo(function IncidentHeatmap({ data }: { data: AnalyticsStats["incidentHeatmap"] }) {
  const max = Math.max(...data.map((d) => d.value), 1)
  return (
    <div className="space-y-1">
      {DAYS.map((day, di) => (
        <div key={day} className="flex items-center gap-2">
          <span className="w-9 text-right text-[9px] uppercase tracking-wider text-text-muted">{day}</span>
          <div className="grid flex-1 grid-cols-[repeat(24,minmax(0,1fr))] gap-[3px]">
            {data.filter((d) => d.day === di).map((d) => {
              const intensity = d.value === 0 ? 0 : 0.15 + (d.value / max) * 0.85
              return (
                <motion.div
                  key={`${d.day}-${d.hour}`}
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: (d.hour / 24) * 0.4 }}
                  title={`${day} ${d.hour}:00 — ${d.value} events`}
                  className="aspect-square rounded-[3px]"
                  style={{
                    background: d.value === 0 ? "rgba(255,255,255,0.03)" : `rgba(239,68,68,${intensity})`,
                    boxShadow: d.value > 0 ? `0 0 6px rgba(239,68,68,${intensity * 0.5})` : undefined,
                  }}
                />
              )
            })}
          </div>
        </div>
      ))}
      <div className="mt-2 flex items-center justify-end gap-2 text-[9px] text-text-muted">
        <span>fewer</span>
        <div className="flex gap-1">
          {[0, 3, 6, 9].map((v) => (
            <span key={v} className="h-2 w-2 rounded-[2px]" style={{ background: v === 0 ? "rgba(255,255,255,0.03)" : `rgba(239,68,68,${0.15 + (v / 9) * 0.85})` }} />
          ))}
        </div>
        <span>more</span>
      </div>
    </div>
  )
})

function PolicyEffectiveness({ data }: { data: AnalyticsStats["policyEffectiveness"] }) {
  const max = Math.max(...data.map((d) => d.detected), 1)
  return (
    <div className="space-y-2.5">
      {data.map((p, i) => (
        <div key={p.policyName}>
          <div className="flex items-center justify-between text-[11px]">
            <span className="truncate text-text-secondary">{p.policyName}</span>
            <span className="mono text-accent-light">{p.effectiveness}% effective</span>
          </div>
          <div className="mt-1 flex h-2 overflow-hidden rounded-full bg-white/[0.05]">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(p.detected / max) * 100}%` }}
              transition={{ duration: 0.7, delay: 0.1 + i * 0.06 }}
              className="h-full rounded-l-full bg-status-medium"
            />
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(p.prevented / max) * 100 - (p.detected / max) * 100}%` }}
              transition={{ duration: 0.7, delay: 0.2 + i * 0.06 }}
              className="h-full bg-status-low"
            />
          </div>
          <div className="mt-0.5 flex justify-between text-[9px] text-text-muted">
            <span>{p.detected} detected</span>
            <span>{p.prevented} prevented</span>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<AnalyticsStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [llmUsage, setLlmUsage] = useState<Awaited<ReturnType<typeof api.llmUsage>> | null>(null)
  const monthlyChartRef = useRef<HTMLDivElement>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.analytics()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadUsage = useCallback(async () => {
    try {
      setLlmUsage(await api.llmUsage())
    } catch {
      setLlmUsage(null)
    }
  }, [])

  useEffect(() => {
    load()
    loadUsage()
    const t = setInterval(load, 20000)
    return () => clearInterval(t)
  }, [load, loadUsage])

  const avgPipeline = useMemo(() => {
    if (!stats?.pipelineDuration.length) return 0
    return Math.round(stats.pipelineDuration.reduce((a, p) => a + p.ms, 0) / stats.pipelineDuration.length)
  }, [stats])

  const maxLatency = useMemo(() => Math.max(...(stats?.agentLatency.map((a) => a.latency) ?? [1])), [stats])

  const downloadCSV = () => {
    if (!stats) return
    const sections: string[] = []
    const addSection = (title: string, rows: Array<Record<string, unknown>>) => {
      sections.push(title)
      if (rows.length === 0) return
      const cols = Object.keys(rows[0])
      sections.push(cols.join(","))
      for (const r of rows) sections.push(cols.map((c) => String(r[c] ?? "")).join(","))
      sections.push("")
    }
    addSection("Monthly Threats", stats.monthlyThreats)
    addSection("Weekly Threats", stats.weeklyThreats)
    addSection("Hourly Attacks", stats.hourlyAttacks)
    addSection("Department Comparison", stats.departmentComparison)
    addSection("Policy Comparison", stats.policyComparison)
    addSection("Risk Evolution", stats.riskEvolution)
    addSection("Risk Forecast", stats.riskForecast)
    addSection("Incident Heatmap", stats.incidentHeatmap)
    addSection("Policy Effectiveness", stats.policyEffectiveness)
    addSection("Detection Distribution", stats.detectionDistribution)
    addSection("Agent Latency", stats.agentLatency)
    addSection("Detection Accuracy", stats.detectionAccuracyTrend)
    addSection("Compliance Score Trend", stats.complianceScoreTrend)
    addSection("Compliance Trend", stats.complianceTrend)
    const blob = new Blob([sections.join("\n")], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `sentinelx-analytics-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  const downloadPNG = () => {
    const svg = monthlyChartRef.current?.querySelector("svg")
    if (!svg) return
    const clone = svg.cloneNode(true) as SVGElement
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    const size = { w: Math.max(svg.clientWidth, 480), h: Math.max(svg.clientHeight, 300) }
    const serialized = new XMLSerializer().serializeToString(clone)
    const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(serialized)}`
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement("canvas")
      canvas.width = size.w
      canvas.height = size.h
      const ctx = canvas.getContext("2d")
      if (!ctx) return
      ctx.fillStyle = "#131316"
      ctx.fillRect(0, 0, size.w, size.h)
      ctx.drawImage(img, 0, 0, size.w, size.h)
      const a = document.createElement("a")
      a.href = canvas.toDataURL("image/png")
      a.download = `sentinelx-monthly-threats-${new Date().toISOString().slice(0, 10)}.png`
      a.click()
    }
    img.src = dataUrl
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-4 w-80" />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Skeleton className="h-72 rounded-xl" />
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
        <BarChart3 className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">Analytics engine unreachable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <Zap className="h-3 w-3" /> Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Analytics"
        description="Deep-dive telemetry across threats, policies, departments, and agent performance — every chart animated with brush zoom."
        actions={
          <div className="flex items-center gap-2">
            <button onClick={downloadPNG} className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-xs font-medium text-text-secondary transition-all hover:border-accent/50 hover:text-accent-light">
              <Download className="h-3.5 w-3.5" /> PNG
            </button>
            <button onClick={downloadCSV} className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-xs font-medium text-text-secondary transition-all hover:border-accent/50 hover:text-accent-light">
              <Download className="h-3.5 w-3.5" /> CSV
            </button>
            <Badge variant="success">7-day window</Badge>
          </div>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Avg Pipeline Duration", value: avgPipeline, suffix: "ms", icon: Clock, tone: "text-accent-light" },
          { label: "Risk Peaks (30d)", value: Math.max(...stats.riskEvolution.map((r) => r.score)), suffix: "/100", icon: TrendingUp, tone: "text-status-high" },
          { label: "Peak LLM Latency", value: maxLatency, suffix: "ms", icon: Gauge, tone: "text-status-medium" },
          { label: "Policy Packs Monitored", value: stats.policyComparison.length, suffix: "", icon: ShieldCheck, tone: "text-status-low" },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card card-glow p-4">
            <s.icon className="h-4 w-4 text-accent-light" />
            <p className="mt-2 text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
            <p className={cn("mono mt-1 text-2xl font-semibold", s.tone)}>{s.value}{s.suffix}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Monthly threats */}
        <ChartCard title="Monthly Threats" icon={BarChart3} delay={0.05} badge="brush to zoom">
          <div ref={monthlyChartRef}>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={stats.monthlyThreats}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
                <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Bar dataKey="blocked" name="Blocked" radius={[4, 4, 0, 0]} fill="#ef4444" isAnimationActive animationDuration={900} />
                <Bar dataKey="allowed" name="Allowed" radius={[4, 4, 0, 0]} fill="#0ea79c" isAnimationActive animationDuration={900} />
                <Brush dataKey="label" height={28} stroke="#0b827a" fill="rgba(11,130,122,0.08)" travellerWidth={8} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Hourly attacks */}
        <ChartCard title="Hourly Attack Distribution" icon={TrendingUp} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={stats.hourlyAttacks}>
              <defs>
                <linearGradient id="hourGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f97316" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} tick={{ fill: "#63636b", fontSize: 10 }} interval={3} />
              <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelFormatter={(h) => `${h}:00`} labelStyle={{ color: "#a1a1aa" }} />
              <Area type="monotone" dataKey="attacks" stroke="#f97316" strokeWidth={2} fill="url(#hourGrad)" isAnimationActive animationDuration={1000} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Weekly threats */}
        <ChartCard title="Weekly Threat Volume" icon={CalendarClock} delay={0.05}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.weeklyThreats}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 11 }} />
              <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
              <Bar dataKey="threats" name="Threats" radius={[4, 4, 0, 0]} isAnimationActive animationDuration={900}>
                {stats.weeklyThreats.map((_, i) => (
                  <Cell key={i} fill={["#ef4444", "#f97316", "#eab308", "#0ea79c", "#3b82f6", "#22c55e"][i % 6]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Department comparison */}
        <ChartCard title="Department Comparison" icon={Filter} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.departmentComparison} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="department" type="category" width={110} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
              <Bar dataKey="riskIndex" name="Risk Index" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={900}>
                {stats.departmentComparison.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk evolution */}
        <ChartCard title="Risk Evolution" icon={LineChartIcon} delay={0.05}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={stats.riskEvolution}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="point" tick={{ fill: "#63636b", fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}/100`, "risk"]} />
              <Line type="monotone" dataKey="score" stroke="#0ea79c" strokeWidth={2} dot={{ r: 2, fill: "#0ea79c" }} isAnimationActive animationDuration={1000} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Detection distribution */}
        <ChartCard title="Detection Distribution" icon={PieChartIcon} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={stats.detectionDistribution} dataKey="count" nameKey="type" innerRadius={55} outerRadius={85} paddingAngle={3} stroke="none" isAnimationActive animationDuration={900}>
                {stats.detectionDistribution.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#fafafa" }} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Policy comparison */}
        <ChartCard title="Policy Comparison" icon={ShieldCheck} delay={0.05}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.policyComparison}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="policyName" tick={{ fill: "#63636b", fontSize: 9 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
              <Bar dataKey="count" name="Violations" radius={[4, 4, 0, 0]} fill="#eab308" isAnimationActive animationDuration={900} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Agent latency */}
        <ChartCard title="Agent Latency" icon={Clock} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.agentLatency} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} horizontal={false} />
              <XAxis type="number" hide />
              <YAxis dataKey="agent" type="category" width={110} tick={{ fill: "#63636b", fontSize: 10 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}ms`, "latency"]} />
              <Bar dataKey="latency" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={900}>
                {stats.agentLatency.map((_, i) => (
                  <Cell key={i} fill={["#0ea79c", "#3b82f6", "#eab308", "#f97316", "#a855f7", "#22c55e", "#ef4444", "#ec4899"][i % 8]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Pipeline duration */}
        <ChartCard title="Pipeline Duration (per scan)" icon={Clock} delay={0.05}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={stats.pipelineDuration}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 10 }} />
              <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}ms`, "duration"]} />
              <Area type="monotone" dataKey="ms" stroke="#3b82f6" strokeWidth={2} fill="rgba(59,130,246,0.15)" isAnimationActive animationDuration={1000} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Compliance trend radar */}
        <ChartCard title="Compliance Trend" icon={ShieldCheck} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={stats.complianceTrend} outerRadius={90}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 10 }} />
              <Radar name="Compliance" dataKey="v" stroke="#0ea79c" fill="#0ea79c" fillOpacity={0.25} isAnimationActive animationDuration={1000} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}%`, "score"]} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk forecast */}
        <ChartCard title="Risk Trend Forecast" icon={TrendingUp} delay={0.05} badge="14-day projection">
          <ResponsiveContainer width="100%" height={240}>
            <ComposedChart data={stats.riskForecast}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="point" tick={{ fill: "#63636b", fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}/100`, "risk"]} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
              <Line dataKey="upper" stroke="rgba(14,167,156,0.2)" strokeWidth={1} dot={false} isAnimationActive animationDuration={1000} />
              <Line dataKey="lower" stroke="rgba(14,167,156,0.2)" strokeWidth={1} dot={false} isAnimationActive animationDuration={1000} />
              <Line dataKey="actual" name="Actual" stroke="#3b82f6" strokeWidth={2} dot={{ r: 2, fill: "#3b82f6" }} isAnimationActive animationDuration={1000} />
              <Line dataKey="forecast" name="Forecast" stroke="#0ea79c" strokeWidth={2} strokeDasharray="6 4" dot={false} isAnimationActive animationDuration={1000} />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Incident heatmap */}
        <ChartCard title="Incident Heatmap (7d × 24h)" icon={CalendarClock} delay={0.1}>
          <MemoIncidentHeatmap data={stats.incidentHeatmap} />
        </ChartCard>

        {/* Policy effectiveness */}
        <ChartCard title="Policy Effectiveness" icon={ShieldCheck} delay={0.05}>
          <PolicyEffectiveness data={stats.policyEffectiveness} />
        </ChartCard>

        {/* Detection accuracy trend */}
        <ChartCard title="Detection Accuracy" icon={Zap} delay={0.1}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={stats.detectionAccuracyTrend}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 11 }} />
              <YAxis domain={[90, 100]} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}%`, "accuracy"]} />
              <Line type="monotone" dataKey="accuracy" stroke="#22c55e" strokeWidth={2} dot={{ r: 3, fill: "#22c55e" }} isAnimationActive animationDuration={1000} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Compliance score trend */}
        <ChartCard title="Compliance Score Trend" icon={TrendingDown} delay={0.05}>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={stats.complianceScoreTrend}>
              <defs>
                <linearGradient id="compGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0ea79c" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#0ea79c" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 11 }} />
              <YAxis domain={[60, 100]} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}%`, "score"]} />
              <Area type="monotone" dataKey="score" stroke="#0ea79c" strokeWidth={2} fill="url(#compGrad)" isAnimationActive animationDuration={1000} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* LLM Usage */}
      {llmUsage && (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <Gauge className="h-4 w-4 text-accent-light" /> LLM Gateway Usage
            </h3>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{llmUsage.provider}</Badge>
              {llmUsage.usage.simulated ? <Badge variant="info">simulated</Badge> : <Badge variant="success">live</Badge>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            {[
              { label: "Requests", value: llmUsage.usage.requests.toLocaleString(), icon: Gauge },
              { label: "Prompt tokens", value: llmUsage.usage.promptTokens.toLocaleString(), icon: Cpu },
              { label: "Completion tokens", value: llmUsage.usage.completionTokens.toLocaleString(), icon: Cpu },
              { label: "Total tokens", value: llmUsage.usage.totalTokens.toLocaleString(), icon: BarChart3 },
              { label: "Est. cost", value: `$${llmUsage.usage.estimatedCostUsd.toFixed(4)}`, icon: TrendingUp },
            ].map((m) => (
              <div key={m.label} className="rounded-lg border border-border-default bg-white/[0.02] p-3.5">
                <m.icon className="h-4 w-4 text-accent-light" />
                <p className="mt-2 text-[10px] uppercase tracking-wider text-text-muted">{m.label}</p>
                <p className="mono mt-1 text-xl font-semibold text-text-primary">{m.value}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
