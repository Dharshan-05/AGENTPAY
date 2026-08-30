"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Globe,
  HardDrive,
  HeartPulse,
  Loader2,

  Server,
  ShieldCheck,
  Timer,
  Wifi,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { api, ApiError } from "@/lib/api"

interface ServiceCard {
  name: string
  icon: React.ComponentType<{ className?: string }>
  status: "healthy" | "degraded" | "down" | "loading"
  metrics: Array<{ label: string; value: string; unit?: string }>
  lastCheck: string
}

const SERVICE_CONFIG: Array<{
  name: string
  icon: React.ComponentType<{ className?: string }>
  serviceId: string
  color: string
}> = [
  { name: "MongoDB", icon: Database, serviceId: "mongodb", color: "text-green-500" },
  { name: "Redis", icon: HardDrive, serviceId: "redis", color: "text-red-500" },
  { name: "Cloudinary", icon: Globe, serviceId: "cloudinary", color: "text-blue-500" },
  { name: "Slack", icon: Activity, serviceId: "slack", color: "text-purple-500" },
  { name: "Resend", icon: Activity, serviceId: "resend", color: "text-orange-500" },
  { name: "OpenRouter", icon: Zap, serviceId: "openrouter", color: "text-yellow-500" },
  { name: "Sentry", icon: AlertTriangle, serviceId: "sentry", color: "text-pink-500" },
  { name: "PostHog", icon: Activity, serviceId: "posthog", color: "text-cyan-500" },
  { name: "System", icon: Server, serviceId: "system", color: "text-indigo-500" },
]

export default function ExecutiveSecurityCenter() {
  const [services, setServices] = useState<ServiceCard[]>(() =>
    SERVICE_CONFIG.map((s) => ({
      name: s.name,
      icon: s.icon,
      status: "loading" as const,
      metrics: [],
      lastCheck: "Checking...",
    }))
  )

  const [systemMetrics, setSystemMetrics] = useState({
    uptime: "0s",
    memory: "0%",
    cpu: "0%",
    apiHealth: "0%",
    activeAgents: 8,
    threatsBlocked24h: 0,
  })

  const fetchService = async (config: typeof SERVICE_CONFIG[0]) => {
    try {
      const start = performance.now()
      const data = await api.health(config.serviceId)
      const latency = Math.round(performance.now() - start)

      let status: "healthy" | "degraded" | "down" = "healthy"
      let metrics: ServiceCard["metrics"] = []

      if (data.available === false || data.healthy === false) {
        status = "degraded"
      }

      switch (config.name) {
        case "MongoDB":
          metrics = [
            { label: "Mode", value: data.mode ?? "connected" },
            { label: "Latency", value: latency.toString(), unit: "ms" },
            { label: "Collections", value: data.collections?.toString() ?? "—" },
          ]
          break
        case "Redis":
          metrics = [
            { label: "Status", value: data.status ?? "ready" },
            { label: "Latency", value: latency.toString(), unit: "ms" },
            { label: "Memory", value: data.memory?.toString() ?? "—", unit: "MB" },
            { label: "Cache Hit", value: data.hitRatio?.toString() ?? "—", unit: "%" },
          ]
          break
        case "Cloudinary":
          metrics = [
            { label: "Storage", value: data.storage?.toString() ?? "—", unit: "GB" },
            { label: "Uploads", value: data.uploads?.toString() ?? "—" },
            { label: "Health", value: data.healthy ? "OK" : "Degraded" },
          ]
          break
        case "Slack":
          metrics = [
            { label: "Last Notify", value: data.lastNotification ?? "—" },
            { label: "Status", value: data.status ?? "OK" },
          ]
          break
        case "Resend":
          metrics = [
            { label: "Emails Today", value: data.emailsToday?.toString() ?? "0" },
            { label: "Delivery", value: data.deliveryStatus ?? "OK" },
          ]
          break
        case "OpenRouter":
          metrics = [
            { label: "Connected", value: data.connected ? "Yes" : "No" },
            { label: "Model", value: data.currentModel ?? "—" },
            { label: "Fallback", value: data.fallbackModel ?? "—" },
            { label: "Requests", value: data.requests?.toString() ?? "0" },
            { label: "Tokens", value: data.tokens?.toString() ?? "0" },
            { label: "Cost", value: data.cost?.toString() ?? "0", unit: "$" },
            { label: "Latency", value: data.latency?.toString() ?? "0", unit: "ms" },
          ]
          break
        case "Sentry":
          metrics = [
            { label: "Errors 24h", value: data.errors24h?.toString() ?? "0" },
            { label: "Health", value: data.health ?? "OK" },
          ]
          break
        case "PostHog":
          metrics = [
            { label: "Active Users", value: data.activeUsers?.toString() ?? "0" },
            { label: "Sessions", value: data.sessions?.toString() ?? "0" },
            { label: "Events", value: data.events?.toString() ?? "0" },
          ]
          break
        case "System":
          metrics = [
            { label: "Uptime", value: data.uptime ?? "—" },
            { label: "Memory", value: data.memory?.toString() ?? "—", unit: "%" },
            { label: "CPU", value: data.cpu?.toString() ?? "—", unit: "%" },
            { label: "API Health", value: data.apiHealth?.toString() ?? "—", unit: "%" },
          ]
          break
      }
      return {
        name: config.name,
        icon: config.icon,
        status,
        metrics,
        lastCheck: new Date().toLocaleTimeString(),
      }
    } catch (error) {
      return {
        name: config.name,
        icon: config.icon,
        status: "down" as const,
        metrics: [{ label: "Error", value: "Service Unavailable" }],
        lastCheck: new Date().toLocaleTimeString(),
      }
    }
  }

  const fetchAll = async () => {
    const results = await Promise.all(SERVICE_CONFIG.map(fetchService))
    setServices(results)

    const system = results.find((s) => s.name === "System")
    if (system) {
      const uptime = system.metrics.find((m) => m.label === "Uptime")?.value
      const memory = system.metrics.find((m) => m.label === "Memory")?.value
      const cpu = system.metrics.find((m) => m.label === "CPU")?.value
      const apiHealth = system.metrics.find((m) => m.label === "API Health")?.value
      setSystemMetrics({
        uptime: uptime ?? "—",
        memory: memory ?? "—",
        cpu: cpu ?? "—",
        apiHealth: apiHealth ?? "—",
        activeAgents: 8,
        threatsBlocked24h: 0,
      })
    }
  }

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: ServiceCard["status"]) => {
    switch (status) {
      case "healthy":
        return <CheckCircle2 className="h-4 w-4 text-status-low" />
      case "degraded":
        return <Activity className="h-4 w-4 text-status-medium" />
      case "down":
        return <AlertTriangle className="h-4 w-4 text-status-high" />
      case "loading":
        return <Loader2 className="h-4 w-4 text-text-muted animate-spin" />
    }
  }

  const getStatusText = (status: ServiceCard["status"]) => {
    switch (status) {
      case "healthy":
        return "Healthy"
      case "degraded":
        return "Degraded"
      case "down":
        return "Down"
      case "loading":
        return "Checking..."
    }
  }

  const getStatusColor = (status: ServiceCard["status"]) => {
    switch (status) {
      case "healthy":
        return "text-status-low"
      case "degraded":
        return "text-status-medium"
      case "down":
        return "text-status-high"
      case "loading":
        return "text-text-muted"
    }
  }

  const healthyCount = services.filter((s) => s.status === "healthy").length
  const totalCount = services.length
  const securityScore = Math.round((healthyCount / totalCount) * 100)

  return (
    <div className="min-h-screen bg-bg-primary">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Executive Security Center</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Real-time enterprise security posture across all integrated services
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 rounded-lg bg-bg-tertiary px-3 py-1.5">
              <span className="text-xs font-medium text-text-secondary">Security Score</span>
              <span className={cn("mono text-lg font-bold", securityScore >= 80 ? "text-status-low" : securityScore >= 60 ? "text-status-medium" : "text-status-high")}>
                {securityScore}/100
              </span>
            </div>
            <Link
              href="/dashboard"
              className="rounded-lg border border-border-strong px-4 py-2 text-sm font-medium text-text-secondary hover:border-accent/50 hover:text-text-primary"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* System Overview */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6 mb-8">
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">Uptime</p>
                <p className="mono mt-1 text-2xl font-bold text-text-primary">{systemMetrics.uptime}</p>
              </div>
              <HeartPulse className="h-6 w-6 text-status-low" />
            </div>
          </div>
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">Memory Usage</p>
                <p className="mono mt-1 text-2xl font-bold text-text-primary">{systemMetrics.memory}</p>
              </div>
              <HardDrive className="h-6 w-6 text-accent-light" />
            </div>
          </div>
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">CPU Usage</p>
                <p className="mono mt-1 text-2xl font-bold text-text-primary">{systemMetrics.cpu}</p>
              </div>
              <Timer className="h-6 w-6 text-accent-light" />
            </div>
          </div>
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">API Health</p>
                <p className="mono mt-1 text-2xl font-bold text-status-low">{systemMetrics.apiHealth}</p>
              </div>
              <HeartPulse className="h-6 w-6 text-status-low" />
            </div>
          </div>
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">Active Agents</p>
                <p className="mono mt-1 text-2xl font-bold text-text-primary">{systemMetrics.activeAgents}</p>
              </div>
              <Activity className="h-6 w-6 text-status-low" />
            </div>
          </div>
          <div className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-text-muted">Threats Blocked (24h)</p>
                <p className="mono mt-1 text-2xl font-bold text-status-low">{systemMetrics.threatsBlocked24h}</p>
              </div>
              <ShieldCheck className="h-6 w-6 text-status-low" />
            </div>
          </div>
        </div>

        {/* Service Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <div
              key={service.name}
              className={cn(
                "glass-card p-5 relative overflow-hidden",
                service.status === "healthy" && "border-status-low/30",
                service.status === "degraded" && "border-status-medium/30",
                service.status === "down" && "border-status-high/30",
              )}
            >
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15">
                    <service.icon className="h-5 w-5 text-accent-light" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-text-primary">{service.name}</h3>
                    <p className="text-xs text-text-muted">Last checked: {service.lastCheck}</p>
                  </div>
                </div>
                <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", getStatusColor(service.status))}>
                  {getStatusIcon(service.status)}
                  <span className="ml-1">{getStatusText(service.status)}</span>
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {service.metrics.map((metric, i) => (
                  <div key={i} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                    <p className="text-[10px] uppercase tracking-wider text-text-muted">{metric.label}</p>
                    <p className={cn("mono mt-1 text-base font-semibold", metric.label === "Status" && metric.value === "ready" ? "text-status-low" : "text-text-primary")}>
                      {metric.value}
                      {metric.unit && <span className="ml-1 text-[10px] text-text-muted">{metric.unit}</span>}
                    </p>
                  </div>
                ))}
              </div>

              {service.metrics.length === 0 && service.status !== "loading" && (
                <div className="mt-4 text-center text-xs text-text-muted">
                  No detailed metrics available
                </div>
              )}
            </div>
          ))}
        </div>

        {/* System Health Summary */}
        <div className="mt-8 glass-card p-6">
          <h2 className="text-lg font-semibold text-text-primary mb-4">System Health Summary</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-border-default bg-white/[0.02] p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-text-muted">Overall Security Score</p>
                  <p className={cn("mono mt-1 text-3xl font-bold", securityScore >= 80 ? "text-status-low" : securityScore >= 60 ? "text-status-medium" : "text-status-high")}>
                    {securityScore}/100
                  </p>
                </div>
                <ShieldCheck className="h-8 w-8 text-status-low" />
              </div>
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-text-muted">Services Healthy</span>
                  <span className="font-medium text-text-primary">{healthyCount} / {totalCount}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-text-muted">Services Degraded</span>
                  <span className="font-medium text-status-medium">
                    {services.filter((s) => s.status === "degraded").length}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-text-muted">Services Down</span>
                  <span className="font-medium text-status-high">
                    {services.filter((s) => s.status === "down").length}
                  </span>
                </div>
              </div>
            </div>
            <div className="rounded-lg border border-border-default bg-white/[0.02] p-4">
              <p className="text-xs uppercase tracking-wider text-text-muted mb-3">Quick Actions</p>
              <div className="space-y-2">
                <Link
                  href="/dashboard/intelligence"
                  className="flex items-center justify-between rounded-lg border border-border-strong px-3 py-2 text-sm text-text-secondary hover:border-accent/50 hover:text-text-primary"
                >
                  <span>View Threat Intelligence</span>
                  <Wifi className="h-4 w-4 text-text-muted" />
                </Link>
                <Link
                  href="/dashboard/audit"
                  className="flex items-center justify-between rounded-lg border border-border-strong px-3 py-2 text-sm text-text-secondary hover:border-accent/50 hover:text-text-primary"
                >
                  <span>View Audit Log</span>
                  <Wifi className="h-4 w-4 text-text-muted" />
                </Link>
                <Link
                  href="/dashboard/incidents"
                  className="flex items-center justify-between rounded-lg border border-border-strong px-3 py-2 text-sm text-text-secondary hover:border-accent/50 hover:text-text-primary"
                >
                  <span>View Incidents</span>
                  <Wifi className="h-4 w-4 text-text-muted" />
                </Link>
              </div>
            </div>
            <div className="rounded-lg border border-border-default bg-white/[0.02] p-4">
              <p className="text-xs uppercase tracking-wider text-text-muted mb-3">System Resources</p>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-text-muted">Memory</span>
                    <span className="font-mono text-text-primary">{systemMetrics.memory}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-border-default overflow-hidden">
                    <div className="h-full bg-status-low w-1/2" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-text-muted">CPU</span>
                    <span className="font-mono text-text-primary">{systemMetrics.cpu}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-border-default overflow-hidden">
                    <div className="h-full bg-accent-light w-1/3" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-text-muted">API Health</span>
                    <span className="font-mono text-status-low">{systemMetrics.apiHealth}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-border-default overflow-hidden">
                    <div className="h-full bg-status-low w-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}