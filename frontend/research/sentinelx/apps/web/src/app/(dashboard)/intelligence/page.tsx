"use client"

import { memo, useCallback, useEffect, useState } from "react"
import { motion } from "framer-motion"
import {
  Brain,
  FileWarning,
  Flame,
  KeyRound,
  Map,
  RefreshCw,
  ShieldAlert,
  Users,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { api } from "@/lib/api"
import type { DashboardStats } from "@/types"
import { Badge, PageHeader, SeverityBadge } from "@/components/ui/primitives"
import { CountUp, Skeleton } from "@/components/ui/motion"
import { ThreatIntelFeed } from "@/components/ui/threat-intel-feed"
import { cn } from "@/lib/utils"

const tooltipStyle = {
  background: "#1c1c21",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  fontSize: 12,
} as const;

const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"];

const ThreatHeatmap = memo(function ThreatHeatmap({ data }: { data: DashboardStats["hourlyTrend"] }) {
  const max = Math.max(...data.map((d) => d.attacks), 1);
  const cellColor = (v: number) => {
    if (v === 0) return "rgba(255,255,255,0.03)";
    const ratio = v / max;
    if (ratio < 0.25) return "rgba(34,197,94,0.4)";
    if (ratio < 0.5) return "rgba(234,179,8,0.5)";
    if (ratio < 0.75) return "rgba(249,115,22,0.6)";
    return "rgba(239,68,68,0.75)";
  };
  return (
    <div className="grid grid-cols-6 gap-2">
      {data.map((d, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.02 }}
          className="flex flex-col items-center gap-1 rounded-lg p-2"
          style={{ background: cellColor(d.attacks) }}
          title={`${String(d.hour).padStart(2, "0")}:00 — ${d.attacks} attack(s)`}
        >
          <span className="mono text-[10px] font-semibold text-text-primary">{d.attacks}</span>
          <span className="text-[8px] uppercase tracking-wider text-text-muted">{String(d.hour).padStart(2, "0")}h</span>
        </motion.div>
      ))}
    </div>
  )
});

const ExecutiveSummary = memo(function ExecutiveSummary({ stats }: { stats: DashboardStats }) {
  const totalRisky = stats.riskDistribution.critical + stats.riskDistribution.high + stats.riskDistribution.medium;
  const avgRiskScore = stats.riskScore;
  const posture = avgRiskScore >= 60 ? "DEGRADED" : avgRiskScore >= 35 ? "ELEVATED" : "STABLE";

  const summary = [
    { label: "Overall Posture", value: posture, tone: avgRiskScore >= 60 ? "text-status-critical" : avgRiskScore >= 35 ? "text-status-medium" : "text-status-low" },
    { label: "Total Prompts Audited", value: stats.totalPrompts.toLocaleString(), tone: "text-text-primary" },
    { label: "Intercepted Threats", value: stats.blockedPrompts.toLocaleString(), tone: "text-status-critical" },
    { label: "Policy Violations (24h)", value: stats.violations24h.toLocaleString(), tone: "text-status-high" },
    { label: "Detection Accuracy", value: `${stats.detectionAccuracy}%`, tone: "text-status-low" },
    { label: "Active Incidents", value: stats.activeIncidents.toLocaleString(), tone: stats.activeIncidents > 5 ? "text-status-critical" : "text-status-low" },
  ];

  return (
    <div className="glass-card card-glow p-6">
      <div className="mb-4 flex items-center gap-2">
        <Brain className="h-4 w-4 text-accent-light" />
        <h2 className="text-sm font-semibold">Executive Summary</h2>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {summary.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-lg border border-border-default bg-white/[0.02] p-3"
          >
            <p className="text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
            <p className={cn("mono mt-1 text-lg font-semibold", s.tone)}>{s.value}</p>
          </motion.div>
        ))}
      </div>
      <p className="mt-4 rounded-lg border border-accent/20 bg-accent/5 px-4 py-3 text-[11px] leading-relaxed text-text-secondary">
        SentinelX processed <span className="mono text-accent-light">{stats.totalPrompts.toLocaleString()} prompts</span> across all gateways. 
        {totalRisky > 0 ? (
          <> <span className="mono text-status-high">{totalRisky} risky requests</span> required intervention — the most common trigger was{" "}
          <span className="text-text-primary">{stats.topCategories[0]?.category ?? "N/A"}</span>, and the top violated policy was{" "}
          <span className="text-text-primary">{stats.topViolatedPolicies[0]?.policyName ?? "N/A"}</span>. Compliance health currently sits at{" "}
          <span className="mono text-accent-light">{stats.complianceHealth}%</span>.</>
        ) : (
          <> No significant threats detected. The perimeter is stable.</>
        )}
      </p>
    </div>
  )
});

const DepartmentRiskChart = memo(function DepartmentRiskChart({ data }: { data: DashboardStats["departmentRisk"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
        <XAxis type="number" domain={[0, 100]} hide />
        <YAxis dataKey="department" type="category" width={90} tick={{ fill: "#63636b", fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Bar dataKey="riskIndex" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={900}>
          {data.map((_, i) => (
            <Cell key={i} fill={i === 0 ? "#ef4444" : i === 1 ? "#f97316" : i === 2 ? "#eab308" : "#0b827a"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
});

const WeeklyTrendChart = memo(function WeeklyTrendChart({ data }: { data: DashboardStats["weeklyTrend"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="weekGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
        <XAxis dataKey="day" tick={{ fill: "#63636b", fontSize: 11 }} />
        <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Area type="monotone" dataKey="attacks" stroke="#ef4444" strokeWidth={2} fill="url(#weekGrad)" isAnimationActive animationDuration={1000} />
      </AreaChart>
    </ResponsiveContainer>
  )
});

const AttackCategoriesChart = memo(function AttackCategoriesChart({ data }: { data: DashboardStats["topCategories"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="category" innerRadius={55} outerRadius={85} paddingAngle={3} stroke="none" isAnimationActive animationDuration={900}>
          {data.map((_, i) => (
            <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#fafafa" }} />
        <Legend wrapperStyle={{ fontSize: 10 }} />
      </PieChart>
    </ResponsiveContainer>
  )
});

const MostTriggeredRules = memo(function MostTriggeredRules({ rules }: { rules: DashboardStats["topViolatedPolicies"] }) {
  if (rules.length === 0) return <p className="py-8 text-center text-xs text-text-muted">No policy violations in this window</p>;
  return (
    <div className="space-y-2.5">
      {rules.map((r, i) => (
        <motion.div
          key={r.policyName}
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.06 }}
          className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-3"
        >
          <SeverityBadge severity={r.severity} />
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-medium text-text-primary">{r.policyName}</p>
            <p className="text-[10px] text-text-muted">{r.regulation}</p>
          </div>
          <span className="mono text-sm font-semibold text-status-high">{r.count}</span>
        </motion.div>
      ))}
    </div>
  )
});

const TopSecretTypes = memo(function TopSecretTypes({ types }: { types: DashboardStats["topSecretTypes"] }) {
  return (
    <div className="space-y-2.5">
      {types.map((t, i) => {
        const max = types[0]?.count ?? 1;
        return (
          <div key={t.type} className="flex items-center gap-3">
            <span className="mono w-5 text-[11px] text-text-muted">{i + 1}</span>
            <div className="flex-1">
              <div className="flex items-center justify-between text-xs">
                <span className="truncate text-text-secondary">{t.type}</span>
                <span className="mono text-text-primary">{t.count}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(t.count / max) * 100}%` }}
                  transition={{ duration: 0.7, delay: i * 0.05 }}
                  className="h-full rounded-full bg-gradient-to-r from-accent-dark to-accent-light"
                />
              </div>
            </div>
          </div>
        )
      })}
      {types.length === 0 && <p className="py-8 text-center text-xs text-text-muted">No secret types detected</p>}
    </div>
  )
});

const HourlyTrendChart = memo(function HourlyTrendChart({ data }: { data: DashboardStats["hourlyTrend"] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
        <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} tick={{ fill: "#63636b", fontSize: 10 }} interval={2} />
        <YAxis tick={{ fill: "#63636b", fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} labelFormatter={(h) => `${h}:00`} labelStyle={{ color: "#a1a1aa" }} />
        <Line type="monotone" dataKey="attacks" stroke="#0b827a" strokeWidth={2} dot={{ r: 2, fill: "#0b827a" }} isAnimationActive animationDuration={1000} />
      </LineChart>
    </ResponsiveContainer>
  )
});

export default function IntelligencePage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const d = await api.dashboard()
      setStats(d)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 12000)
    return () => clearInterval(t)
  }, [load])

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
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Skeleton className="h-96 rounded-xl" />
          <Skeleton className="h-96 rounded-xl" />
        </div>
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
        <p className="text-sm text-text-secondary">API temporarily unavailable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <RefreshCw className="h-3 w-3" /> Retry connection
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Intelligence Center"
        description="Correlated threat telemetry across every gateway event — heatmaps, attack categories, policy exposure, and department risk."
        actions={<Badge variant="success">Auto-refreshing · 12s</Badge>}
      />

      <ExecutiveSummary stats={stats} />

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Hourly Attack Trend */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <div className="mb-3">
            <h2 className="text-sm font-semibold">Hourly Attack Trend</h2>
            <p className="text-[11px] text-text-muted">risky prompts by hour of day</p>
          </div>
          <HourlyTrendChart data={stats.hourlyTrend} />
        </motion.div>

        {/* Weekly Trend */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-5">
          <div className="mb-3">
            <h2 className="text-sm font-semibold">Weekly Threat Volume</h2>
            <p className="text-[11px] text-text-muted">attacks per day, last 7 days</p>
          </div>
          <WeeklyTrendChart data={stats.weeklyTrend} />
        </motion.div>

        {/* Attack Categories */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="glass-card card-glow p-5">
          <div className="mb-3">
            <h2 className="text-sm font-semibold">Attack Categories</h2>
            <p className="text-[11px] text-text-muted">detected secret types breakdown</p>
          </div>
          <AttackCategoriesChart data={stats.topCategories} />
        </motion.div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Threat Heatmap */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Threat Heatmap</h2>
              <p className="text-[11px] text-text-muted">24-hour activity density · green = quiet · red = attack spike</p>
            </div>
            <Map className="h-4 w-4 text-text-muted" />
          </div>
          <ThreatHeatmap data={stats.hourlyTrend} />
        </motion.div>

        {/* Risk Distribution Radial */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-5">
          <div className="mb-3">
            <h2 className="text-sm font-semibold">Risk Concentration</h2>
            <p className="text-[11px] text-text-muted">critical share of risky events</p>
          </div>
          <div className="h-[220px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart innerRadius="50%" outerRadius="80%" data={[
                { name: "Critical", value: stats.riskDistribution.critical, fill: "#ef4444" },
                { name: "High", value: stats.riskDistribution.high, fill: "#f97316" },
                { name: "Medium", value: stats.riskDistribution.medium, fill: "#eab308" },
                { name: "Low", value: stats.riskDistribution.low, fill: "#0b827a" },
              ]} startAngle={90} endAngle={-270}>
                <RadialBar background={{ fill: "rgba(255,255,255,0.03)" }} dataKey="value" cornerRadius={6} />
                <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#fafafa" }} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Most Triggered Rules */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
          <div className="mb-3 flex items-center gap-2">
            <Flame className="h-4 w-4 text-status-high" />
            <h2 className="text-sm font-semibold">Most Triggered Rules</h2>
          </div>
          <MostTriggeredRules rules={stats.topViolatedPolicies} />
        </motion.div>

        {/* Top Secret Types */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }} className="glass-card card-glow p-5">
          <div className="mb-3 flex items-center gap-2">
            <KeyRound className="h-4 w-4 text-accent-light" />
            <h2 className="text-sm font-semibold">Top Secret Types</h2>
          </div>
          <TopSecretTypes types={stats.topSecretTypes} />
        </motion.div>

        {/* Department Risk */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="glass-card card-glow p-5">
          <div className="mb-3 flex items-center gap-2">
            <Users className="h-4 w-4 text-status-medium" />
            <h2 className="text-sm font-semibold">Department Risk</h2>
          </div>
          {stats.departmentRisk.length > 0 ? (
            <DepartmentRiskChart data={stats.departmentRisk} />
          ) : (
            <p className="py-8 text-center text-xs text-text-muted">No department data yet</p>
          )}
        </motion.div>
      </div>

      {/* Policy violations breakdown */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card card-glow p-5">
        <div className="mb-3 flex items-center gap-2">
          <FileWarning className="h-4 w-4 text-status-medium" />
          <h2 className="text-sm font-semibold">Policy Violations · Compliance Impact</h2>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: "Critical events", value: stats.riskDistribution.critical, cls: "text-status-critical" },
            { label: "High events", value: stats.riskDistribution.high, cls: "text-status-high" },
            { label: "Medium events", value: stats.riskDistribution.medium, cls: "text-status-medium" },
            { label: "Low events", value: stats.riskDistribution.low, cls: "text-status-low" },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border border-border-default bg-white/[0.02] p-4 text-center">
              <p className="text-[10px] uppercase tracking-wider text-text-muted">{s.label}</p>
              <CountUp value={s.value} className={cn("mono mt-1 text-2xl font-semibold", s.cls)} />
            </div>
          ))}
        </div>
      </motion.div>

      {/* Threat intelligence feed */}
      <ThreatIntelFeed />
    </div>
  )
}