"use client"

import { memo, useCallback, useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  FileWarning,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  AlertTriangle,
  Target,
  Zap,
  ClipboardCheck,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts"
import { api, timeAgo, formatTime, THREAT_COLORS } from "@/lib/api"
import type { AgentHealth, DashboardStats } from "@/types"
import { Badge, DecisionBadge, RiskGauge, SeverityBadge } from "@/components/ui/primitives"
import { CountUp, Skeleton } from "@/components/ui/motion"
import { cn } from "@/lib/utils"

const PIE_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};
const THREAT_PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"];

const tooltipStyle = {
  background: "#1c1c21",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  fontSize: 12,
} as const;

const RiskPieChart = memo(function RiskPieChart({ data }: { data: Array<{ name: string; value: number }> }) {
  return (
    <ResponsiveContainer width="55%" height={180}>
      <PieChart>
        <Pie data={data} dataKey="value" innerRadius={45} outerRadius={70} paddingAngle={4} stroke="none" isAnimationActive animationDuration={900}>
          {data.map((d) => (
            <Cell key={d.name} fill={PIE_COLORS[d.name] ?? "#63636b"} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#fafafa" }} />
      </PieChart>
    </ResponsiveContainer>
  )
});

const RiskTrendChart = memo(function RiskTrendChart({ data }: { data: Array<{ name: string; score: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0b827a" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#0b827a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="name" hide />
        <YAxis domain={[0, 100]} hide />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Area type="monotone" dataKey="score" stroke="#0ea79c" strokeWidth={2} fill="url(#riskGrad)" isAnimationActive animationDuration={1000} />
      </AreaChart>
    </ResponsiveContainer>
  )
});

const WeeklyTrendChart = memo(function WeeklyTrendChart({ data }: { data: Array<{ day: string; attacks: number }> }) {
  const maxAttacks = Math.max(...data.map(d => d.attacks), 1);
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
        <XAxis type="number" domain={[0, maxAttacks * 1.3]} hide />
        <YAxis dataKey="day" type="category" width={50} tick={{ fill: "#63636b", fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Bar dataKey="attacks" fill="#0b827a" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={800} />
      </BarChart>
    </ResponsiveContainer>
  )
});

const HourlyHeatmapChart = memo(function HourlyHeatmapChart({ data }: { data: Array<{ hour: number; attacks: number }> }) {
  const maxAttacks = Math.max(...data.map(d => d.attacks), 1);
  return (
    <ResponsiveContainer width="100%" height={160}>
      <div className="flex items-end justify-center gap-1 h-full px-2">
        {data.map((d, i) => (
          <motion.div
            key={i}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: `${Math.max((d.attacks / maxAttacks) * 100, d.attacks > 0 ? 8 : 4)}%`, opacity: 1 }}
            transition={{ delay: i * 0.03, duration: 0.5 }}
            className="flex-1 flex flex-col items-center justify-end rounded-t transition-all"
            style={{ background: d.attacks > 0 ? `linear-gradient(to top, #ef4444, #f97316)` : "rgba(255,255,255,0.03)" }}
          >
            <div className="w-full" style={{ height: `${Math.max((d.attacks / maxAttacks) * 100, d.attacks > 0 ? 8 : 4)}%` }} />
            <span className="text-[9px] text-text-muted mt-1 mono">{d.hour % 4 === 0 ? `${String(d.hour).padStart(2, '0')}:00` : " "}</span>
          </motion.div>
        ))}
      </div>
    </ResponsiveContainer>
  )
});

const SecurityTrendChart = memo(function SecurityTrendChart({ data }: { data: number[] }) {
  const chartData = data.map((score, i) => ({ name: `D${i + 1}`, score }));
  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={chartData}>
        <defs>
          <linearGradient id="secGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0b827a" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#0b827a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} />
        <XAxis dataKey="name" hide />
        <YAxis domain={[0, 100]} hide />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Line type="monotone" dataKey="score" stroke="#0ea79c" strokeWidth={2} dot={false} isAnimationActive animationDuration={1200} />
        <Area type="monotone" dataKey="score" stroke="none" fill="url(#secGrad)" isAnimationActive animationDuration={1200} />
      </LineChart>
    </ResponsiveContainer>
  )
});

const DepartmentRiskChart = memo(function DepartmentRiskChart({ data }: { data: Array<{ department: string; riskIndex: number; avgScore: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
        <XAxis type="number" domain={[0, 100]} hide />
        <YAxis dataKey="department" type="category" width={100} tick={{ fill: "#63636b", fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#a1a1aa" }} />
        <Bar dataKey="riskIndex" fill="#f97316" radius={[0, 4, 4, 0]} isAnimationActive animationDuration={800} />
      </BarChart>
    </ResponsiveContainer>
  )
});

const SecretTypesChart = memo(function SecretTypesChart({ data }: { data: Array<{ type: string; count: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="type" innerRadius={50} outerRadius={80} paddingAngle={3} stroke="none" isAnimationActive animationDuration={900}>
          {data.map((_, i) => (
            <Cell key={i} fill={THREAT_PIE_COLORS[i % THREAT_PIE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#fafafa" }} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
});

const MetricCard = memo(function MetricCard({ 
  title, 
  value, 
  sub, 
  icon: Icon, 
  trend, 
  trendUp, 
  accent = "text-accent-light",
  size = "md"
}: { 
  title: string; 
  value: React.ReactNode; 
  sub?: string; 
  icon: React.ElementType; 
  trend?: string; 
  trendUp?: boolean; 
  accent?: string;
  size?: "sm" | "md" | "lg";
}) {
  const padding = size === "lg" ? "p-6" : size === "sm" ? "p-3" : "p-4";
  const iconSize = size === "lg" ? "h-12 w-12" : size === "sm" ? "h-7 w-7" : "h-9 w-9";
  const valueSize = size === "lg" ? "text-3xl" : size === "sm" ? "text-lg" : "text-2xl";
  
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className={`glass-card card-glow ${padding}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted">{title}</p>
          <p className={`mono mt-1.5 font-semibold ${valueSize} text-text-primary`}>{value}</p>
          {sub && <p className="mt-1 text-[11px] text-text-muted">{sub}</p>}
        </div>
        <div className={cn("flex items-center justify-center rounded-lg bg-white/[0.03]", accent)}>
          <Icon className={iconSize} />
        </div>
      </div>
      {trend && (
        <div className={cn("mt-2 flex items-center gap-1 text-[11px] font-medium", trendUp ? "text-status-low" : "text-status-critical")}>
          <span>{trend}</span>
          <span className="text-text-muted">vs previous period</span>
        </div>
      )}
    </motion.div>
  )
});

const LiveActivityFeed = memo(function LiveActivityFeed({ events }: { events: DashboardStats["recentEvents"] }) {
  return (
    <div className="space-y-3">
      {events.slice(0, 10).map((ev, i) => (
        <motion.div
          key={ev.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="flex items-center gap-3 p-3 rounded-lg border border-border-subtle/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-[9px] font-semibold text-accent-light flex-shrink-0">
            {ev.user?.name ? ev.user.name.split(" ").map(n => n[0]).slice(0,2).join("").toUpperCase() : "AI"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-text-secondary truncate">{ev.user?.name ?? "System"}</span>
              <span className="text-[10px] text-text-muted">{ev.user?.department ? `· ${ev.user.department}` : ""}</span>
              <span className="mono text-[10px] text-text-muted">{formatTime(ev.timestamp)}</span>
            </div>
            <p className="mt-0.5 text-xs text-text-muted truncate">{ev.prompt}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`mono text-xs font-semibold ${THREAT_COLORS[ev.threatLevel]}`}>{ev.riskScore}</span>
            <DecisionBadge decision={ev.decision} />
          </div>
        </motion.div>
      ))}
      {events.length === 0 && (
        <div className="text-center py-8 text-xs text-text-muted">
          No recent activity
        </div>
      )}
    </div>
  )
});

const TopViolatedPolicies = memo(function TopViolatedPolicies({ policies }: { policies: DashboardStats["topViolatedPolicies"] }) {
  return (
    <div className="space-y-3">
      {policies.slice(0, 5).map((p, i) => (
        <motion.div
          key={p.policyName}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="flex items-center justify-between p-3 rounded-lg border border-border-subtle/50 bg-white/[0.02]"
        >
          <div className="flex items-center gap-3">
            <SeverityBadge severity={p.severity} />
            <div>
              <p className="text-xs font-medium text-text-primary truncate max-w-[200px]">{p.policyName}</p>
              <p className="text-[10px] text-text-muted">{p.regulation} · {p.count} violation{p.count !== 1 ? "s" : ""}</p>
            </div>
          </div>
          <span className="mono text-sm font-semibold text-status-high">{p.count}</span>
        </motion.div>
      ))}
      {policies.length === 0 && (
        <div className="text-center py-8 text-xs text-text-muted">
          No policy violations
        </div>
      )}
    </div>
  )
});

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [agents, setAgents] = useState<AgentHealth[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const load = useCallback(async () => {
    try {
      const [dashRes, agentRes] = await Promise.allSettled([api.dashboard(), api.agents()])
      if (dashRes.status === "fulfilled") setStats(dashRes.value)
      else setStats(null)
      if (agentRes.status === "fulfilled") setAgents(agentRes.value)
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
      setLastRefresh(new Date())
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 10000)
    return () => clearInterval(t)
  }, [load])

  const trendData = useMemo(
    () => (stats?.promptsTrend ?? []).map((score, i) => ({ name: `T${i + 1}`, score })),
    [stats],
  )

  const riskPie = useMemo(
    () =>
      stats
        ? [
            { name: "Critical", value: stats.riskDistribution.critical },
            { name: "High", value: stats.riskDistribution.high },
            { name: "Medium", value: stats.riskDistribution.medium },
            { name: "Low", value: stats.riskDistribution.low },
          ].filter((d) => d.value > 0)
        : [],
    [stats],
  )

  const PIE_COLORS: Record<string, string> = {
    Critical: "#ef4444",
    High: "#f97316",
    Medium: "#eab308",
    Low: "#22c55e",
  }

  const securityTrendData = useMemo(
    () => (stats?.securityTrend ?? []).slice(-30),
    [stats],
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-end justify-between">
          <div className="space-y-2">
            <Skeleton className="h-7 w-56" />
            <Skeleton className="h-4 w-72" />
          </div>
          <Skeleton className="h-9 w-32 rounded-lg" />
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
        <ShieldAlert className="h-10 w-10 text-status-critical" />
        <p className="text-sm text-text-secondary">SentinelX API temporarily unavailable</p>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <RefreshCw className="h-3 w-3" /> Retry connection
        </button>
      </div>
    )
  }

  const safeRequests = stats.safeRequests ?? Math.max(0, stats.totalPrompts - stats.blockedPrompts)
  const orgRiskIndex = stats.departmentRisk.length > 0 
    ? Math.round(stats.departmentRisk.reduce((acc, d) => acc + d.riskIndex, 0) / stats.departmentRisk.length)
    : 0;
  const globalSecurityScore = Math.max(0, 100 - stats.riskScore);

  function threatLabel(score: number): string {
    if (score >= 80) return "CRITICAL"
    if (score >= 60) return "HIGH"
    if (score >= 35) return "MEDIUM"
    if (score >= 15) return "LOW"
    return "SAFE"
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold tracking-tight">Executive Security Center</h1>
            <Badge variant="success">Live</Badge>
          </div>
          <p className="mt-1 text-sm text-text-secondary">
            Real-time AI governance across all LLM gateways · updated {lastRefresh ? timeAgo(lastRefresh) : "…"}
          </p>
        </div>
        <button onClick={load} className="tech-chip cursor-pointer hover:border-accent">
          <RefreshCw className="h-3 w-3" /> Refresh
        </button>
      </div>

      {/* Top Row - Key Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6"
      >
        <MetricCard 
          title="Global Security Score" 
          value={<CountUp value={globalSecurityScore} suffix="/100" />} 
          sub="composite security posture" 
          icon={ShieldCheck} 
          trend="+2.1%" 
          trendUp={true} 
          accent="text-status-low"
          size="lg"
        />
        <MetricCard 
          title="Organization Risk Index" 
          value={<CountUp value={orgRiskIndex} suffix="%" />} 
          sub="dept-weighted risk exposure" 
          icon={Target} 
          trend="-1.3%" 
          trendUp={true} 
          accent="text-status-high"
          size="lg"
        />
        <MetricCard 
          title="Active Incidents" 
          value={<CountUp value={stats.activeIncidents} />} 
          sub={stats.criticalIncidents > 0 ? `${stats.criticalIncidents} critical` : "last 24 hours"} 
          icon={AlertTriangle} 
          trend={stats.activeIncidents > 10 ? "+12%" : "-5%"} 
          trendUp={stats.activeIncidents <= 10} 
          accent={stats.activeIncidents > 10 ? "text-status-critical" : "text-status-low"}
        />
        <MetricCard 
          title="Blocked Prompts Today" 
          value={<CountUp value={stats.blockedPrompts} />} 
          sub="intercepted at gateway" 
          icon={ShieldAlert} 
          trend="+8.1%" 
          trendUp={false} 
          accent="text-status-critical"
        />
        <MetricCard 
          title="Safe Requests" 
          value={<CountUp value={safeRequests} />} 
          sub="allowed to reach the model" 
          icon={CheckCircle2} 
          trend="+4.6%" 
          trendUp={true} 
          accent="text-status-low"
        />
        <MetricCard 
          title="Compliance Health" 
          value={<CountUp value={stats.complianceHealth} suffix="%" />} 
          sub="policy adherence rate" 
          icon={ClipboardCheck} 
          trend="+1.2%" 
          trendUp={true} 
          accent="text-accent-light"
        />
      </motion.div>

      {/* Second Row - Operational Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0, transition: { delay: 0.05 } }}
        className="grid grid-cols-2 gap-4 lg:grid-cols-4"
      >
        <MetricCard 
          title="Agent Health" 
          value={agents.length > 0 ? <CountUp value={Math.round((agents.filter(a => a.status === "healthy").length / agents.length) * 100)} suffix="%" /> : <span className="text-text-muted">—</span>} 
          sub={`${agents.length || 8} agents · ${agents.filter(a => a.status === "healthy").length} healthy`} 
          icon={Bot} 
          trend={agents.length > 0 && agents.some(a => a.status !== "healthy") ? "attention" : "optimal"} 
          trendUp={agents.every(a => a.status === "healthy")} 
          accent="text-status-low"
        />
        <MetricCard 
          title="Detection Accuracy" 
          value={<CountUp value={stats.detectionAccuracy} suffix="%" />} 
          sub="secret & PII detection" 
          icon={Target} 
          trend="+0.3%" 
          trendUp={true} 
          accent="text-accent-light"
        />
        <MetricCard 
          title="Avg Response Time" 
          value={<CountUp value={stats.avgResponseTime} suffix="ms" />} 
          sub="pipeline latency p95" 
          icon={Zap} 
          trend="-5ms" 
          trendUp={true} 
          accent="text-status-low"
        />
        <MetricCard 
          title="Violations 24h" 
          value={<CountUp value={stats.violations24h} />} 
          sub="policy violations detected" 
          icon={FileWarning} 
          trend="-3.2%" 
          trendUp={true} 
          accent="text-status-high"
        />
      </motion.div>

      {/* Main Grid */}
      <div className="grid gap-4 lg:grid-cols-12">
        {/* Left Column - Risk Overview */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }} className="lg:col-span-5 space-y-4">
          <div className="glass-card card-glow p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Enterprise Risk Score</h2>
                <p className="text-[11px] text-text-muted">composite threat assessment</p>
              </div>
            </div>
            <div className="flex items-center justify-center gap-6">
              <RiskGauge score={stats.riskScore} size="lg" />
              <div className="text-center">
                <div className={`text-xs font-semibold uppercase tracking-wider ${THREAT_COLORS[threatLabel(stats.riskScore)]}`}>
                  {threatLabel(stats.riskScore)}
                </div>
                <p className="mt-2 text-[11px] leading-relaxed text-text-muted max-w-xs">
                  Composite score from severity, data sensitivity, intent, policy violations & historical behaviour
                </p>
              </div>
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Threat Distribution</h2>
                <p className="text-[11px] text-text-muted">last 50 events</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <RiskPieChart data={riskPie} />
              <div className="flex-1 space-y-2.5">
                {riskPie.map((d) => (
                  <div key={d.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full" style={{ background: PIE_COLORS[d.name] ?? "#63636b" }} />
                      <span className="text-text-secondary">{d.name}</span>
                    </div>
                    <span className="mono font-medium text-text-primary">{d.value}</span>
                  </div>
                ))}
                {riskPie.length === 0 && <p className="text-xs text-text-muted">No risk events yet</p>}
              </div>
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Prompt Risk Trend</h2>
              <p className="text-[11px] text-text-muted">risk score per event</p>
            </div>
            <RiskTrendChart data={trendData} />
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Security Trend (30 Days)</h2>
              <p className="text-[11px] text-text-muted">daily average risk score</p>
            </div>
            <SecurityTrendChart data={securityTrendData} />
          </div>
        </motion.div>

        {/* Middle Column - Threat Intelligence */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.15 } }} className="lg:col-span-4 space-y-4">
          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Detection Categories</h2>
              <p className="text-[11px] text-text-muted">most frequent secret types</p>
            </div>
            <div className="space-y-2.5">
              {stats.topCategories.map((c, i) => (
                <div key={c.category} className="flex items-center gap-3">
                  <span className="w-5 mono text-[11px] text-text-muted">{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="truncate text-text-secondary">{c.category}</span>
                      <span className="mono text-text-primary">{c.count}</span>
                    </div>
                    <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(c.count / Math.max(stats.topCategories[0]?.count, 1)) * 100}%` }}
                        transition={{ duration: 0.6, delay: 0.2 + i * 0.05 }}
                        className="h-full rounded-full bg-gradient-to-r from-accent-dark to-accent-light"
                      />
                    </div>
                  </div>
                </div>
              ))}
              {stats.topCategories.length === 0 && <p className="text-xs text-text-muted">No detections yet</p>}
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Secret Types Distribution</h2>
              <p className="text-[11px] text-text-muted">detected entity breakdown</p>
            </div>
            <SecretTypesChart data={stats.topSecretTypes} />
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Hourly Attack Heatmap</h2>
              <p className="text-[11px] text-text-muted">threat activity by hour (24h)</p>
            </div>
            <HourlyHeatmapChart data={stats.hourlyTrend} />
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold">Weekly Attack Trend</h2>
              <p className="text-[11px] text-text-muted">threat volume by day</p>
            </div>
            <WeeklyTrendChart data={stats.weeklyTrend} />
          </div>
        </motion.div>

        {/* Right Column - Policies, Departments, Activity */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.2 } }} className="lg:col-span-3 space-y-4">
          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Top Violated Policies</h2>
                <p className="text-[11px] text-text-muted">last 24 hours</p>
              </div>
            </div>
            <TopViolatedPolicies policies={stats.topViolatedPolicies} />
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Department Risk Index</h2>
                <p className="text-[11px] text-text-muted">risk exposure by org unit</p>
              </div>
            </div>
            <DepartmentRiskChart data={stats.departmentRisk} />
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Agent Pipeline Health</h2>
                <p className="text-[11px] text-text-muted">8 agents · real-time status</p>
              </div>
              <Badge variant="success">All Healthy</Badge>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {agents.map((agent, i) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1, transition: { delay: 0.3 + i * 0.05 } }}
                  whileHover={{ y: -2, borderColor: "rgba(11,130,122,0.4)", boxShadow: "0 0 20px rgba(11,130,122,0.12)" }}
                  className="rounded-lg border border-border-default bg-white/[0.02] p-3"
                >
                  <div className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-status-low heartbeat" />
                    <span className="truncate text-xs font-medium text-text-primary">{agent.name}</span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-[10px] leading-snug text-text-muted">{agent.responsibility}</p>
                  <p className="mono mt-1.5 text-[10px] text-accent-light">{agent.responseTime}ms · {agent.successRate}% ok</p>
                </motion.div>
              ))}
            </div>
            {agents.length === 0 && (
              <p className="rounded-lg border border-dashed border-border-default px-3 py-4 text-center text-xs text-text-muted">
                No agent telemetry available
              </p>
            )}
            <div className="mt-4 flex items-center justify-between rounded-lg border border-accent/25 bg-accent/5 px-4 py-3">
              <div className="flex items-center gap-2 text-xs text-text-secondary">
                <Sparkles className="h-4 w-4 text-accent-light" />
                <span>Prompt flow: <span className="mono text-accent-light">User → Inspector → Detection → Policy → Risk → Rewriter → LLM → Audit → Memory</span></span>
              </div>
              <a href="/scanner" className="flex items-center gap-1 text-xs font-medium text-accent-light hover:text-accent">
                Open scanner <ArrowRight className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>

          <div className="glass-card card-glow p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Live Activity Feed</h2>
                <p className="text-[11px] text-text-muted">real-time gateway events</p>
              </div>
              <a href="/activity" className="flex items-center gap-1 text-xs font-medium text-accent-light hover:text-accent">
                View all <ArrowRight className="h-3.5 w-3.5" />
              </a>
            </div>
            <LiveActivityFeed events={stats.recentEvents} />
          </div>
        </motion.div>
      </div>
    </div>
  )
}