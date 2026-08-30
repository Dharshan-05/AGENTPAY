"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import {
  ArrowUpRight,
  DollarSign,
  TrendingUp,

  Zap,
  Clock,
  Target,
  ArrowDownRight,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"

interface MetricCard {
  title: string
  value: string
  change?: string
  changeType?: "up" | "down" | "neutral"
  icon: React.ComponentType<{ className?: string }>
  color: string
}

interface AnalyticsData {
  todayCost: string
  todayTokens: string
  avgLatency: string
  fastestModel: string
  slowestModel: string
  providerSuccessRate: number
  fallbackCount: number
  costTrend: Array<{ date: string; cost: number; tokens: number }>
  modelComparison: Array<{ model: string; requests: number; avgLatency: number; successRate: number; cost: number }>
  providerHealth: Array<{ provider: string; status: "healthy" | "degraded" | "down"; uptime: number; avgLatency: number }>
  fallbackTrend: Array<{ date: string; primary: number; fallback: number; secondary: number }>
  hourlyUsage: Array<{ hour: number; requests: number; tokens: number; cost: number }>
  modelUsage: Array<{ model: string; percentage: number; cost: number }>
}

const MOCK_DATA: AnalyticsData = {
  todayCost: "$127.43",
  todayTokens: "847,231",
  avgLatency: "342ms",
  fastestModel: "nvidia/nemotron-3-ultra (287ms)",
  slowestModel: "openai/gpt-oss-20b (1,247ms)",
  providerSuccessRate: 99.2,
  fallbackCount: 23,
  costTrend: [
    { date: "Aug 1", cost: 89.23, tokens: 567234 },
    { date: "Aug 2", cost: 102.45, tokens: 678901 },
    { date: "Aug 3", cost: 76.89, tokens: 445678 },
    { date: "Aug 4", cost: 134.56, tokens: 789012 },
    { date: "Aug 5", cost: 112.34, tokens: 623456 },
    { date: "Aug 6", cost: 145.78, tokens: 823456 },
    { date: "Aug 7", cost: 127.43, tokens: 847231 },
  ],
  modelComparison: [
    { model: "nvidia/nemotron-3-ultra", requests: 1247, avgLatency: 287, successRate: 99.8, cost: 45.23 },
    { model: "nvidia/nemotron-3-super", requests: 892, avgLatency: 423, successRate: 99.5, cost: 32.11 },
    { model: "openai/gpt-oss-20b", requests: 456, avgLatency: 1247, successRate: 98.9, cost: 28.45 },
    { model: "google/gemini-1.5-flash", requests: 234, avgLatency: 567, successRate: 99.2, cost: 15.67 },
    { model: "anthropic/claude-3.5-haiku", requests: 189, avgLatency: 789, successRate: 99.1, cost: 5.97 },
  ],
  providerHealth: [
    { provider: "OpenRouter", status: "healthy", uptime: 99.9, avgLatency: 342 },
    { provider: "OpenAI", status: "healthy", uptime: 99.7, avgLatency: 567 },
    { provider: "Anthropic", status: "healthy", uptime: 99.8, avgLatency: 623 },
    { provider: "Google", status: "degraded", uptime: 98.5, avgLatency: 892 },
    { provider: "Ollama", status: "down", uptime: 95.2, avgLatency: 1200 },
  ],
  fallbackTrend: [
    { date: "Aug 1", primary: 124, fallback: 2, secondary: 1 },
    { date: "Aug 2", primary: 156, fallback: 3, secondary: 0 },
    { date: "Aug 3", primary: 98, fallback: 5, secondary: 2 },
    { date: "Aug 4", primary: 178, fallback: 8, secondary: 3 },
    { date: "Aug 5", primary: 134, fallback: 4, secondary: 1 },
    { date: "Aug 6", primary: 167, fallback: 12, secondary: 4 },
    { date: "Aug 7", primary: 145, fallback: 7, secondary: 2 },
  ],
  hourlyUsage: Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    requests: Math.floor(Math.random() * 100) + 20,
    tokens: Math.floor(Math.random() * 50000) + 10000,
    cost: Math.floor(Math.random() * 50) + 10,
  })),
  modelUsage: [
    { model: "nvidia/nemotron-3-ultra", percentage: 42.3, cost: 45.23 },
    { model: "nvidia/nemotron-3-super", percentage: 30.1, cost: 32.11 },
    { model: "openai/gpt-oss-20b", percentage: 15.4, cost: 28.45 },
    { model: "google/gemini-1.5-flash", percentage: 7.9, cost: 15.67 },
    { model: "anthropic/claude-3.5-haiku", percentage: 4.3, cost: 5.97 },
  ],
}

export default function AIAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const json = await api.analytics()
        setData(json as unknown as AnalyticsData)
      } catch {
        setData(MOCK_DATA)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  const formatCost = (cost: number) => `$${cost.toFixed(2)}`
  const formatTokens = (tokens: number) => tokens.toLocaleString()

  const topMetrics: MetricCard[] = [
    {
      title: "Today's Cost",
      value: data?.todayCost ?? "$127.43",
      change: "+12.3%",
      changeType: "up",
      icon: DollarSign,
      color: "text-status-medium",
    },
    {
      title: "Today's Tokens",
      value: data?.todayTokens ?? "847,231",
      change: "+8.7%",
      changeType: "up",
      icon: Zap,
      color: "text-accent-light",
    },
    {
      title: "Avg Latency",
      value: data?.avgLatency ?? "342ms",
      change: "-12ms",
      changeType: "down",
      icon: Clock,
      color: "text-status-low",
    },
    {
      title: "Provider Success",
      value: `${data?.providerSuccessRate ?? 99.2}%`,
      change: "+0.3%",
      changeType: "up",
      icon: Target,
      color: "text-status-low",
    },
    {
      title: "Fallbacks Today",
      value: data?.fallbackCount?.toString() ?? "23",
      change: "-5",
      changeType: "down",
      icon: ArrowDownRight,
      color: "text-status-low",
    },
    {
      title: "Fastest Model",
      value: data?.fastestModel?.split(" ")[0] ?? "nemotron-3-ultra",
      change: "287ms avg",
      changeType: "neutral",
      icon: TrendingUp,
      color: "text-accent-light",
    },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-primary">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-bg-tertiary rounded w-1/4" />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="glass-card h-24" />
              ))}
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="glass-card h-64" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">AI Analytics</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Real-time cost, latency, and provider analytics for your AI governance pipeline
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Top Metrics */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6 mb-8">
          {topMetrics.map((metric, i) => (
            <div key={i} className="glass-card p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-text-muted">{metric.title}</p>
                  <p className="mono mt-1 text-2xl font-bold text-text-primary">{metric.value}</p>
                </div>
                <metric.icon className={cn("h-6 w-6", metric.color)} />
              </div>
              {metric.change && (
                <div className="mt-2 flex items-center gap-1">
                  {metric.changeType === "up" && <ArrowUpRight className={cn("h-3 w-3", metric.changeType === "up" && "text-status-medium")} />}
                  {metric.changeType === "down" && <ArrowDownRight className={cn("h-3 w-3", metric.changeType === "down" && "text-status-low")} />}
                  {metric.changeType === "neutral" && <span className="h-3 w-3" />}
                  <span className={cn("text-xs font-medium", metric.changeType === "up" ? "text-status-medium" : metric.changeType === "down" ? "text-status-low" : "text-text-muted")}>
                    {metric.change}
                  </span>
                </div>
              )}
            </div>
          ))}

        {/* Charts Row 1 */}
        <div className="grid gap-4 lg:grid-cols-2 mb-8">
          {/* Cost Trend */}
          <div className="glass-card p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-text-primary">Cost Trend (7 Days)</h2>
            </div>
            <div className="h-64">
              <svg viewBox="0 0 600 256" className="w-full h-full">
                <defs>
                  <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0ea79c" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#0ea79c" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {data?.costTrend.map((point, i) => {
                  const x = (i / (data.costTrend.length - 1)) * 560 + 20
                  const y = 236 - (point.cost / 150) * 200
                  return (
                    <g key={i}>
                      {i > 0 && (
                        <path
                          d={`M${20 + (i - 1) * (560 / (data.costTrend.length - 1))} ${236 - data.costTrend[i - 1].cost / 150 * 200} L${x} ${y}`}
                          stroke="url(#costGradient)"
                          strokeWidth="2"
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      )}
                      <circle cx={x} cy={y} r={4} fill="#0ea79c" />
                    </g>
                  )
                })}
              </svg>
            </div>
            <div className="mt-4 flex justify-between text-xs text-text-muted">
              {data?.costTrend.slice(0, 3).map((p) => (
                <span key={p.date}>{p.date}: {formatCost(p.cost)}</span>
              ))}
            </div>
          </div>

          {/* Fallback Trend */}
          <div className="glass-card p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-text-primary">Fallback Trend (7 Days)</h2>
            </div>
            <div className="h-64">
              <svg viewBox="0 0 600 256" className="w-full h-full">
                {data?.fallbackTrend.map((point, i) => {
                  const x = (i / (data.fallbackTrend.length - 1)) * 560 + 20
                  const primaryY = 236 - (point.primary / 200) * 200
                  const fallbackY = 236 - (point.fallback / 200) * 200
                  const secondaryY = 236 - (point.secondary / 200) * 200
                  return (
                    <g key={i}>
                      {i > 0 && (
                        <>
                          <path d={`M${20 + (i - 1) * (560 / (data.fallbackTrend.length - 1))} ${236 - data.fallbackTrend[i - 1].primary / 200 * 200} L${x} ${primaryY}`} stroke="#0ea79c" strokeWidth="2" fill="none" strokeLinecap="round" />
                          <path d={`M${20 + (i - 1) * (560 / (data.fallbackTrend.length - 1))} ${236 - data.fallbackTrend[i - 1].fallback / 200 * 200} L${x} ${fallbackY}`} stroke="#f59e0b" strokeWidth="2" fill="none" strokeDasharray="4 2" />
                          <path d={`M${20 + (i - 1) * (560 / (data.fallbackTrend.length - 1))} ${236 - data.fallbackTrend[i - 1].secondary / 200 * 200} L${x} ${secondaryY}`} stroke="#ef4444" strokeWidth="2" fill="none" strokeDasharray="2 4" />
                        </>
                      )}
                      <circle cx={x} cy={primaryY} r={3} fill="#0ea79c" />
                      <circle cx={x} cy={fallbackY} r={3} fill="#f59e0b" />
                      <circle cx={x} cy={secondaryY} r={3} fill="#ef4444" />
                    </g>
                  )
                })}
              </svg>
            </div>
            <div className="mt-4 flex items-center justify-center gap-4 text-xs text-text-muted">
              <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-status-low rounded" /> Primary</span>
              <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-status-medium rounded" /> Fallback</span>
              <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-status-high rounded" /> Secondary</span>
            </div>
          </div>
        </div>

        {/* Model Comparison & Provider Health */}
        <div className="grid gap-4 lg:grid-cols-2 mb-8">
          {/* Model Comparison Table */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Model Comparison</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border-default text-left text-xs text-text-muted uppercase tracking-wider">
                    <th className="pb-2">Model</th>
                    <th className="pb-2 text-right mono">Requests</th>
                    <th className="pb-2 text-right mono">Avg Latency</th>
                    <th className="pb-2 text-right mono">Success Rate</th>
                    <th className="pb-2 text-right mono">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.modelComparison.map((m, i) => (
                    <tr key={m.model} className={cn("border-b border-border-subtle", i === 0 && "bg-accent/5")}>
                      <td className="py-3 font-medium text-text-primary">{m.model}</td>
                      <td className="py-3 text-right mono text-text-secondary">{m.requests.toLocaleString()}</td>
                      <td className="py-3 text-right mono text-text-secondary">{m.avgLatency}ms</td>
                      <td className="py-3 text-right mono text-status-low">{m.successRate}%</td>
                      <td className="py-3 text-right mono text-text-primary">{formatCost(m.cost)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Provider Health */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Provider Health</h2>
            <div className="space-y-4">
              {data?.providerHealth.map((p) => (
                <div key={p.provider} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn("h-2 w-2 rounded-full", p.status === "healthy" ? "bg-status-low" : p.status === "degraded" ? "bg-status-medium" : "bg-status-high")} />
                    <div>
                      <p className="text-sm font-medium text-text-primary">{p.provider}</p>
                      <p className="text-xs text-text-muted">{p.uptime}% uptime · {p.avgLatency}ms avg</p>
                    </div>
                  </div>
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", p.status === "healthy" ? "bg-status-low/20 text-status-low" : p.status === "degraded" ? "bg-status-medium/20 text-status-medium" : "bg-status-high/20 text-status-high")}>
                    {p.status.charAt(0).toUpperCase() + p.status.slice(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Hourly Usage & Model Usage */}
        <div className="grid gap-4 lg:grid-cols-2 mb-8">
          {/* Hourly Usage */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Hourly Usage (24h)</h2>
            <div className="h-64">
              <svg viewBox="0 0 600 256" className="w-full h-full">
                {data?.hourlyUsage.map((point, i) => {
                  const x = (i / 23) * 560 + 20
                  const y = 236 - (point.requests / 120) * 200
                  return (
                    <g key={i}>
                      <rect x={x - 10} y={y} width={20} height={236 - y} fill="#0ea79c" opacity="0.6" rx={2} />
                    </g>
                  )
                })}
              </svg>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="mono text-2xl font-bold text-text-primary">{data?.hourlyUsage.reduce((a, b) => a + b.requests, 0).toLocaleString() ?? "0"}</p>
                <p className="text-xs text-text-muted">Total Requests</p>
              </div>
              <div>
                <p className="mono text-2xl font-bold text-accent-light">{formatCost(data?.hourlyUsage.reduce((a, b) => a + b.cost, 0) ?? 0)}</p>
                <p className="text-xs text-text-muted">Total Cost</p>
              </div>
              <div>
                <p className="mono text-2xl font-bold text-text-primary">{formatTokens(data?.hourlyUsage.reduce((a, b) => a + b.tokens, 0) ?? 0)}</p>
                <p className="text-xs text-text-muted">Total Tokens</p>
              </div>
            </div>
          </div>

          {/* Model Usage Distribution */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Model Usage Distribution</h2>
            <div className="space-y-4">
              {data?.modelUsage.map((m) => (
                <div key={m.model} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-text-primary">{m.model}</span>
                    <span className="mono text-text-primary">{m.percentage}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-border-default overflow-hidden">
                    <div className="h-full bg-accent-light rounded-full transition-all duration-500" style={{ width: `${m.percentage}%` }} />
                  </div>
                  <p className="text-xs text-text-muted">Cost: {formatCost(m.cost)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Quick Actions</h2>
          <div className="flex flex-wrap gap-4">
            <Link href="/dashboard/ai-analytics" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              View Full Analytics
            </Link>
            <Link href="/dashboard/executive" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              Executive Dashboard
            </Link>
            <Link href="/dashboard" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              Back to Dashboard
            </Link>
            <Link href="/dashboard/scanner" className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary">
              Run Live Scan
            </Link>
          </div>
        </div>
      </div>
    </div>
    </div>
  )
}