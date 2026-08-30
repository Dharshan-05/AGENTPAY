"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Building2,
  CheckCircle2,
  Clock,
  Cpu,
  DollarSign,
  Eye,
  Gauge,
  Landmark,
  Lightbulb,
  RefreshCw,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { api, timeAgo } from "@/lib/api"
import type { ExecutiveInsight, ExecutiveStats } from "@/types"
import { Badge, SeverityBadge, PageHeader } from "@/components/ui/primitives"
import { CountUp, Skeleton } from "@/components/ui/motion"
import { MaturityGauge } from "@/components/ui/gauges"
import { cn } from "@/lib/utils"

const tooltipStyle = {
  background: "#1c1c21",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  fontSize: 12,
} as const

const DEPT_COLORS = ["#0ea79c", "#3b82f6", "#eab308", "#f97316", "#a855f7", "#22c55e"]

export default function ExecutivePage() {
  const [stats, setStats] = useState<ExecutiveStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState<{ items: ExecutiveInsight[]; model: string | null; simulated: boolean } | null>(null)

  const load = useCallback(async () => {
    try {
      const d = await api.executive()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadInsights = useCallback(async () => {
    try {
      const res = await api.executiveInsights()
      setInsights({ items: res.data, model: res.model, simulated: res.simulated })
    } catch {
      setInsights(null)
    }
  }, [])

  useEffect(() => {
    load()
    loadInsights()
    const t = setInterval(load, 15000)
    return () => clearInterval(t)
  }, [load, loadInsights])

  const kpiCards = useMemo(
    () =>
      stats
        ? [
            { label: "Prompts Audited", value: stats.kpis.promptsAudited, suffix: "", icon: BarChart3, tone: "text-text-primary" },
            { label: "Threats Intercepted", value: stats.kpis.threatsIntercepted, suffix: "", icon: ShieldCheck, tone: "text-status-critical" },
            { label: "Policy Violations", value: stats.kpis.violations, suffix: "", icon: AlertTriangle, tone: "text-status-high" },
            { label: "Active Incidents", value: stats.kpis.activeIncidents, suffix: "", icon: Activity, tone: stats.kpis.activeIncidents > 3 ? "text-status-critical" : "text-status-low" },
            { label: "Detection Accuracy", value: stats.kpis.detectionAccuracy, suffix: "%", icon: Eye, tone: "text-status-low" },
            { label: "Avg Response", value: stats.kpis.avgResponseTime, suffix: "ms", icon: Clock, tone: "text-accent-light" },
          ]
        : [],
    [stats],
  )

  const fmtMoney = (v: number) =>
    v >= 1e6
      ? `$${(v / 1e6).toFixed(1)}M`
      : v >= 1e3
        ? `$${Math.round(v / 1e3)}K`
        : `$${v}`

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-4 w-80" />
          </div>
          <Skeleton className="h-9 w-36 rounded-lg" />
        </div>
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <ShieldAlert className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">API temporarily unavailable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <RefreshCw className="h-3 w-3" /> Retry connection
        </button>
      </div>
    )
  }

  const posture = stats.organizationHealth.label
  const postureTone = stats.organizationHealth.score >= 85 ? "text-status-low" : stats.organizationHealth.score >= 60 ? "text-status-medium" : "text-status-critical"

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive Command Center"
        description="Enterprise-wide AI security posture — a live board for the C-suite and board room."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="success">LIVE</Badge>
            <span className="text-[11px] text-text-muted">Updated {timeAgo(stats.timestamp)}</span>
          </div>
        }
      />

      {/* Hero: Security score + org health + maturity */}
      <div className="grid gap-4 lg:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card card-glow p-6 flex items-center gap-6"
        >
          <MaturityGauge score={stats.maturity.score} label={stats.maturity.label} />
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-wider text-text-muted">Company Security Score</p>
            <p className="mono mt-1 text-4xl font-bold text-text-primary">
              <CountUp value={stats.companySecurityScore} />
            </p>
            <p className={cn("mt-1 text-xs font-medium", postureTone)}>Organization Health · {posture}</p>
            <div className="mt-3 flex items-center gap-2 text-[11px] text-text-muted">
              <Cpu className="h-3.5 w-3.5" />
              {stats.agentsOnline} AI agents · all operational
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.06 } }}
          className="glass-card card-glow p-6"
        >
          <div className="mb-3 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <TrendingUp className="h-4 w-4 text-accent-light" /> Risk Trend
            </h3>
            <Badge variant="outline">last 24 scans</Badge>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={stats.riskTrend}>
              <defs>
                <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0ea79c" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#0ea79c" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="point" hide />
              <YAxis domain={[0, 100]} hide />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}/100`, "risk"]} />
              <Area type="monotone" dataKey="score" stroke="#0ea79c" strokeWidth={2} fill="url(#riskGrad)" isAnimationActive animationDuration={1100} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.12 } }}
          className="glass-card card-glow p-6"
        >
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Gauge className="h-4 w-4 text-accent-light" /> Compliance Status
          </h3>
          <div className="space-y-2.5">
            {stats.complianceStatus.map((c, i) => (
              <motion.div
                key={c.regulation}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 + i * 0.06 }}
                className="flex items-center gap-3"
              >
                <span className="w-20 text-xs font-medium text-text-secondary">{c.regulation}</span>
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05]">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${c.score}%` }}
                    transition={{ duration: 0.8, delay: 0.2 + i * 0.06 }}
                    className="h-full rounded-full bg-gradient-to-r from-accent-dark via-accent to-accent-light"
                  />
                </div>
                <span className="mono w-8 text-right text-[11px] text-text-secondary">{c.score}%</span>
                <CheckCircle2 className="h-3.5 w-3.5 text-status-low" />
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Executive KPI cards */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        {kpiCards.map((k, i) => (
          <motion.div
            key={k.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card card-glow p-4"
          >
            <k.icon className="h-4 w-4 text-accent-light" />
            <p className="mt-2.5 text-[10px] uppercase tracking-wider text-text-muted">{k.label}</p>
            <p className={cn("mono mt-1 text-2xl font-semibold", k.tone)}>
              <CountUp value={k.value} suffix={k.suffix} />
            </p>
          </motion.div>
        ))}
      </div>

      {/* Financial exposure + compliance trend + risk forecast */}
      <div className="grid gap-4 lg:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card card-glow p-6"
        >
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Landmark className="h-4 w-4 text-accent-light" /> Financial Exposure
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] p-3.5">
              <div className="flex items-center gap-2.5">
                <DollarSign className="h-4 w-4 text-status-low" />
                <span className="text-xs text-text-secondary">Loss averted</span>
              </div>
              <span className="mono text-lg font-bold text-text-primary">
                <CountUp value={stats.financialExposure.lossAverted} format={fmtMoney} />
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border-default bg-white/[0.02] p-3.5">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="h-4 w-4 text-status-high" />
                <span className="text-xs text-text-secondary">Regulatory fine exposure</span>
              </div>
              <span className="mono text-lg font-bold text-text-primary">
                <CountUp value={stats.financialExposure.fineExposure} format={fmtMoney} />
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-status-critical/20 bg-status-critical/[0.05] p-3.5">
              <div className="flex items-center gap-2.5">
                <AlertTriangle className="h-4 w-4 text-status-critical" />
                <span className="text-xs text-text-secondary">Avg breach cost</span>
              </div>
              <span className="mono text-lg font-bold text-status-critical">
                <CountUp value={stats.financialExposure.breachCost} format={fmtMoney} />
              </span>
            </div>
            <p className="text-[10px] leading-relaxed text-text-muted">
              Estimated from intercepted threats × industry avg remediation cost and violations × GDPR-tier fine exposure.
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.06 } }}
          className="glass-card card-glow p-6"
        >
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <TrendingUp className="h-4 w-4 text-accent-light" /> Compliance Trend
          </h3>
          <p className="mb-3 text-[10px] text-text-muted">Quarterly enterprise compliance score</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={stats.complianceScoreTrend}>
              <defs>
                <linearGradient id="compGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: "#63636b", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[40, 100]} hide />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any) => [`${v}%`, "score"]} />
              <Area type="monotone" dataKey="score" stroke="#22c55e" strokeWidth={2} fill="url(#compGrad)" isAnimationActive animationDuration={1100} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.12 } }}
          className="glass-card card-glow p-6"
        >
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Cpu className="h-4 w-4 text-accent-light" /> Risk Forecast
          </h3>
          <p className="mb-3 text-[10px] text-text-muted">14-day projection with confidence band</p>
          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={stats.riskForecast}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
              <XAxis dataKey="point" tick={{ fill: "#63636b", fontSize: 9 }} axisLine={false} tickLine={false} tickFormatter={(p) => (p === 24 ? "now" : p === 30 ? "+6d" : p === 37 ? "+13d" : "")} />
              <YAxis domain={[0, 100]} hide />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} formatter={(v: any, n: any) => [v, n === "forecast" ? "forecast" : n === "actual" ? "actual" : "band"]} />
              <Area dataKey="upper" stroke="none" fill="#3b82f6" fillOpacity={0.08} />
              <Area dataKey="lower" stroke="none" fill="#09090b" />
              <Line type="monotone" dataKey="forecast" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 4" dot={false} isAnimationActive animationDuration={1100} />
              <Line type="monotone" dataKey="actual" stroke="#0ea79c" strokeWidth={2} dot={{ r: 2.5, fill: "#0ea79c" }} isAnimationActive animationDuration={1100} />
            </ComposedChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* AI Executive Insights */}
      {insights && insights.items.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card card-glow overflow-hidden"
        >
          <div className="flex items-center justify-between border-b border-border-subtle px-5 py-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <Sparkles className="h-4 w-4 text-accent-light" /> AI Executive Insights
            </h3>
            <div className="flex items-center gap-2">
              {insights.model && <span className="mono text-[10px] text-text-muted">{insights.model}</span>}
              {insights.simulated && <Badge variant="info">simulated</Badge>}
            </div>
          </div>
          <div className="grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-3">
            {insights.items.map((ins, i) => (
              <motion.div
                key={ins.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="rounded-lg border border-border-default bg-white/[0.02] p-3.5"
              >
                <div className="mb-2 flex items-center justify-between gap-2">
                  <span
                    className={cn(
                      "rounded-md px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider",
                      ins.category === "risk" && "bg-critical text-status-critical",
                      ins.category === "trend" && "bg-high text-status-high",
                      ins.category === "compliance" && "bg-medium text-status-medium",
                      ins.category === "recommendation" && "bg-low text-status-low",
                      ins.category === "kpi" && "bg-accent/15 text-accent-light",
                    )}
                  >
                    {ins.category}
                  </span>
                  {ins.severity === "critical" && <AlertTriangle className="h-3.5 w-3.5 text-status-critical" />}
                  {ins.severity === "positive" && <CheckCircle2 className="h-3.5 w-3.5 text-status-low" />}
                </div>
                <p className="text-xs font-semibold text-text-primary">{ins.title}</p>
                <p className="mt-1 text-[10px] leading-relaxed text-text-muted">{ins.summary}</p>
                {ins.metric && (
                  <div className="mt-2 flex items-center gap-2 rounded-md bg-bg-secondary/60 px-2 py-1.5">
                    <span className="text-[9px] uppercase tracking-wider text-text-muted">{ins.metric.label}</span>
                    <span className="mono text-xs font-semibold text-text-primary">{ins.metric.value}</span>
                    {ins.metric.delta && (
                      <span className={cn("mono text-[10px]", ins.metric.delta.startsWith("+") ? "text-status-critical" : "text-status-low")}>
                        {ins.metric.delta}
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Department breakdown */}        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }}
          className="glass-card card-glow p-6 lg:col-span-2"
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <Building2 className="h-4 w-4 text-accent-light" /> Department Security Breakdown
            </h3>
            <Badge variant="outline">risk index</Badge>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats.departmentBreakdown} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.05} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="name" type="category" width={120} tick={{ fill: "#63636b", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
              <Bar dataKey="riskIndex" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={1000}>
                {stats.departmentBreakdown.map((_, i) => (
                  <Cell key={i} fill={DEPT_COLORS[i % DEPT_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Alerts + Recommendations */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }}
          className="space-y-4"
        >
          <div className="glass-card card-glow p-5">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <AlertTriangle className="h-4 w-4 text-status-high" /> Recent Executive Alerts
            </h3>
            <div className="space-y-2">
              {stats.executiveAlerts.slice(0, 4).map((a, i) => (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.06 }}
                  className="flex items-start gap-2.5 rounded-lg border border-border-default bg-white/[0.02] p-2.5"
                >
                  <SeverityBadge severity={a.severity} />
                  <div className="min-w-0">
                    <p className="truncate text-xs font-medium text-text-primary">{a.title}</p>
                    <p className="truncate text-[10px] text-text-muted">{a.source} · {timeAgo(a.createdAt)}</p>
                  </div>
                </motion.div>
              ))}
              {stats.executiveAlerts.length === 0 && <p className="py-4 text-center text-xs text-text-muted">No alerts</p>}
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Lightbulb className="h-4 w-4 text-accent-light" /> Recommendations
            </h3>
            <div className="space-y-2">
              {stats.recommendations.map((r, i) => (
                <motion.div
                  key={r.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.06 }}
                  className="flex items-start gap-2.5 rounded-lg border border-accent/15 bg-accent/[0.04] p-2.5"
                >
                  <Sparkles className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-accent-light" />
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-text-primary">{r.title}</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-text-muted">{r.detail}</p>
                  </div>
                </motion.div>
              ))}
              {stats.recommendations.length === 0 && (
                <p className="rounded-lg border border-dashed border-border-default px-3 py-4 text-center text-xs text-text-muted">
                  No recommendations right now — posture is healthy
                </p>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
