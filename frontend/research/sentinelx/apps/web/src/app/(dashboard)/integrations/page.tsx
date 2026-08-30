"use client"

import { useState } from "react"
import {
  Database,
  Server,
  Zap,
  Mail,
  MessageSquare,
  BarChart3,
  Bug,
  Cloud,
  CreditCard,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  Globe,
  Activity,
  DollarSign,
  Search,
  X,
} from "lucide-react"
import { Badge } from "@/components/ui/primitives"
import { cn } from "@/lib/utils"

interface Integration {
  id: string
  name: string
  category: string
  icon: React.ReactNode
  description: string
  configured: boolean
  healthy: boolean
  latency?: number
  requestsToday?: number
  errors?: number
  lastSync?: string
  version?: string
  docsUrl?: string
  config?: Record<string, any>
  metrics?: Record<string, any>
}

const INTEGRATIONS: Integration[] = [
  {
    id: "postgresql",
    name: "PostgreSQL",
    category: "Database",
    icon: <Database className="h-5 w-5" />,
    description: "Primary relational database for audit logs, policies, and user management",
    configured: true,
    healthy: true,
    latency: 12,
    requestsToday: 45230,
    errors: 0,
    lastSync: "2 min ago",
    version: "15.4",
    docsUrl: "https://docs.sentinelx.dev/integrations/postgresql",
    metrics: { connections: 8, poolUsage: "80%", queryTime: "8ms" },
  },
  {
    id: "mongodb",
    name: "MongoDB Atlas",
    category: "Database",
    icon: <Cloud className="h-5 w-5" />,
    description: "Document database for incidents, reports, and analytics data",
    configured: true,
    healthy: true,
    latency: 24,
    requestsToday: 12450,
    errors: 0,
    lastSync: "1 min ago",
    version: "7.0",
    docsUrl: "https://docs.sentinelx.dev/integrations/mongodb",
    metrics: { connections: 12, storage: "2.4 GB", opsSec: "1.2k" },
  },
  {
    id: "redis",
    name: "Redis",
    category: "Cache",
    icon: <Zap className="h-5 w-5" />,
    description: "High-speed caching for dashboards, sessions, and rate limiting",
    configured: true,
    healthy: true,
    latency: 2,
    requestsToday: 892000,
    errors: 0,
    lastSync: "30 sec ago",
    version: "7.2",
    docsUrl: "https://docs.sentinelx.dev/integrations/redis",
    metrics: { hitRatio: "94%", memory: "45 MB", keys: "12.4k" },
  },
  {
    id: "sentry",
    name: "Sentry",
    category: "Observability",
    icon: <Bug className="h-5 w-5" />,
    description: "Error tracking, performance monitoring, and session replay",
    configured: true,
    healthy: true,
    latency: 45,
    requestsToday: 1240,
    errors: 2,
    lastSync: "5 min ago",
    version: "1.0.0",
    docsUrl: "https://docs.sentinelx.dev/integrations/sentry",
    metrics: { issues: 3, transactions: "98.7%", replays: 156 },
  },
  {
    id: "posthog",
    name: "PostHog",
    category: "Analytics",
    icon: <BarChart3 className="h-5 w-5" />,
    description: "Product analytics, feature flags, and session replay",
    configured: true,
    healthy: true,
    latency: 38,
    requestsToday: 45230,
    errors: 0,
    lastSync: "1 min ago",
    version: "1.14",
    docsUrl: "https://docs.sentinelx.dev/integrations/posthog",
    metrics: { events: "2.1M", flags: 12, replays: 890 },
  },
  {
    id: "cloudinary",
    name: "Cloudinary",
    category: "Storage",
    icon: <Cloud className="h-5 w-5" />,
    description: "Media storage for evidence, compliance reports, and avatars",
    configured: true,
    healthy: true,
    latency: 120,
    requestsToday: 2340,
    errors: 0,
    lastSync: "10 min ago",
    version: "2.0",
    docsUrl: "https://docs.sentinelx.dev/integrations/cloudinary",
    metrics: { storage: "2.4 GB", images: 1250, transformations: "5.2k" },
  },
  {
    id: "razorpay",
    name: "Razorpay",
    category: "Payments",
    icon: <CreditCard className="h-5 w-5" />,
    description: "Subscription billing, invoicing, and payment processing",
    configured: true,
    healthy: true,
    latency: 280,
    requestsToday: 45,
    errors: 0,
    lastSync: "2 hours ago",
    version: "2.9",
    docsUrl: "https://docs.sentinelx.dev/integrations/razorpay",
    metrics: { subscriptions: 3, mrr: "₹4.9L", successRate: "100%" },
  },
  {
    id: "resend",
    name: "Resend",
    category: "Notifications",
    icon: <Mail className="h-5 w-5" />,
    description: "Transactional email delivery for alerts, reports, and billing",
    configured: true,
    healthy: true,
    latency: 320,
    requestsToday: 1240,
    errors: 0,
    lastSync: "30 min ago",
    version: "3.1",
    docsUrl: "https://docs.sentinelx.dev/integrations/resend",
    metrics: { delivered: 1240, bounced: 2, opened: "68%" },
  },
  {
    id: "slack",
    name: "Slack",
    category: "Notifications",
    icon: <MessageSquare className="h-5 w-5" />,
    description: "Real-time incident alerts and compliance notifications",
    configured: true,
    healthy: true,
    latency: 180,
    requestsToday: 890,
    errors: 0,
    lastSync: "5 min ago",
    version: "2.0",
    docsUrl: "https://docs.sentinelx.dev/integrations/slack",
    metrics: { channels: 8, messages: 890, delivered: "99.8%" },
  },
  {
    id: "openai",
    name: "OpenAI",
    category: "AI Providers",
    icon: <Activity className="h-5 w-5" />,
    description: "GPT-4o-mini for AI insights, explanations, and rewriting",
    configured: true,
    healthy: true,
    latency: 850,
    requestsToday: 45230,
    errors: 12,
    lastSync: "1 min ago",
    version: "gpt-4o-mini",
    docsUrl: "https://docs.sentinelx.dev/integrations/openai",
    metrics: { tokens: "12.4M", cost: "$2,450", successRate: "99.97%" },
  },
  {
    id: "anthropic",
    name: "Anthropic Claude",
    category: "AI Providers",
    icon: <Activity className="h-5 w-5" />,
    description: "Claude 3.5 Haiku for compliance summaries and policy recommendations",
    configured: true,
    healthy: true,
    latency: 1200,
    requestsToday: 18920,
    errors: 8,
    lastSync: "2 min ago",
    version: "claude-3.5-haiku",
    docsUrl: "https://docs.sentinelx.dev/integrations/anthropic",
    metrics: { tokens: "8.9M", cost: "$1,890", successRate: "99.95%" },
  },
  {
    id: "gemini",
    name: "Google Gemini",
    category: "AI Providers",
    icon: <Activity className="h-5 w-5" />,
    description: "Gemini 1.5 Flash for threat classification and intent analysis",
    configured: true,
    healthy: true,
    latency: 650,
    requestsToday: 12450,
    errors: 5,
    lastSync: "1 min ago",
    version: "gemini-1.5-flash",
    docsUrl: "https://docs.sentinelx.dev/integrations/gemini",
    metrics: { tokens: "5.6M", cost: "$567", successRate: "99.96%" },
  },
  {
    id: "ollama",
    name: "Ollama (Local)",
    category: "AI Providers",
    icon: <Server className="h-5 w-5" />,
    description: "Local LLM inference for air-gapped environments",
    configured: false,
    healthy: false,
    latency: 0,
    requestsToday: 3420,
    errors: 0,
    lastSync: "Never",
    version: "llama3.1",
    docsUrl: "https://docs.sentinelx.dev/integrations/ollama",
    metrics: { tokens: "1.2M", cost: "$0", status: "Disabled" },
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    category: "AI Providers",
    icon: <Globe className="h-5 w-5" />,
    description: "Multi-provider gateway for model routing and fallback",
    configured: true,
    healthy: true,
    latency: 420,
    requestsToday: 8920,
    errors: 3,
    lastSync: "1 min ago",
    version: "1.0",
    docsUrl: "https://docs.sentinelx.dev/integrations/openrouter",
    metrics: { tokens: "3.4M", cost: "$345", models: 12 },
  },
]

export default function IntegrationsPage() {
  const [search, setSearch] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const categories = ["all", ...new Set(INTEGRATIONS.map(i => i.category))]
  const filtered = INTEGRATIONS.filter(i => {
    const matchesSearch = i.name.toLowerCase().includes(search.toLowerCase()) ||
                          i.description.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = categoryFilter === "all" || i.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const connected = INTEGRATIONS.filter(i => i.configured).length
  const healthy = INTEGRATIONS.filter(i => i.configured && i.healthy).length
  const unhealthy = INTEGRATIONS.filter(i => i.configured && !i.healthy).length
  const totalRequests = INTEGRATIONS.reduce((sum, i) => sum + (i.requestsToday ?? 0), 0)

  const handleRefresh = async () => {
    setRefreshing(true)
    await new Promise(r => setTimeout(r, 1000))
    setRefreshing(false)
  }

  const selected = INTEGRATIONS.find(i => i.id === selectedId)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Enterprise Integrations</h1>
          <p className="mt-1 text-sm text-text-muted">
            Monitor and manage all connected enterprise services
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-sm font-medium text-text-secondary hover:bg-white/[0.05] transition-colors disabled:opacity-60"
          >
            <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-low/15">
              <CheckCircle2 className="h-5 w-5 text-status-low" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">Connected</p>
              <p className="text-2xl font-bold text-text-primary">{connected}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-low/15">
              <Activity className="h-5 w-5 text-status-low" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">Healthy</p>
              <p className="text-2xl font-bold text-text-primary">{healthy}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-critical/15">
              <AlertCircle className="h-5 w-5 text-status-critical" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">Issues</p>
              <p className="text-2xl font-bold text-text-primary">{unhealthy}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15">
              <Zap className="h-5 w-5 text-accent-light" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">Requests Today</p>
              <p className="text-2xl font-bold text-text-primary">{totalRequests.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border-default bg-white/[0.02] p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-high/15">
              <DollarSign className="h-5 w-5 text-status-high" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">MRR</p>
              <p className="text-2xl font-bold text-text-primary">₹4.9L</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
            <input
              type="text"
              placeholder="Search integrations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border-default bg-white/[0.03] text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={e => setCategoryFilter(e.target.value)}
            className="rounded-lg border border-border-default bg-white/[0.03] px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
          >
            {categories.map(c => (
              <option key={c} value={c}>
                {c === "all" ? "All Categories" : c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {filtered.map(integration => (
          <IntegrationCard
            key={integration.id}
            integration={integration}
            selected={selectedId === integration.id}
            onClick={() => setSelectedId(selectedId === integration.id ? null : integration.id)}
          />
        ))}
      </div>

      {/* Detail Panel */}
      {selected && (
        <div role="dialog" aria-modal="true" aria-label={`${selected.name} integration details`} className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm p-4 sm:p-0">
          <div
            className="w-full max-w-2xl max-h-[85vh] overflow-hidden rounded-2xl border border-border-default bg-bg-secondary shadow-2xl animate-slide-up"
          >
            <div className="flex items-center justify-between border-b border-border-subtle px-6 py-4">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-lg",
                  selected.configured && selected.healthy && "bg-status-low/15",
                  selected.configured && !selected.healthy && "bg-status-critical/15",
                  !selected.configured && "bg-text-muted/15",
                )}>
                  {selected.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">{selected.name}</h3>
                  <p className="text-sm text-text-muted">{selected.category}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedId(null)}
                aria-label="Close integration details"
                className="p-1 rounded hover:bg-white/[0.04]"
              >
                <X className="h-5 w-5 text-text-muted" />
              </button>
            </div>

            <div className="max-h-[60vh] overflow-y-auto p-6 space-y-6">
              {/* Status */}
              <div className="flex items-center gap-3 rounded-lg border border-border-default bg-white/[0.02] p-4">
                <div className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full",
                  selected.configured && selected.healthy && "bg-status-low/15",
                  selected.configured && !selected.healthy && "bg-status-critical/15",
                  !selected.configured && "bg-text-muted/15",
                )}>
                  {selected.configured && selected.healthy && <CheckCircle2 className="h-5 w-5 text-status-low" />}
                  {selected.configured && !selected.healthy && <XCircle className="h-5 w-5 text-status-critical" />}
                  {!selected.configured && <AlertCircle className="h-5 w-5 text-text-muted" />}
                </div>
                <div>
                  <p className="font-medium text-text-primary">
                    {selected.configured ? (selected.healthy ? "Healthy" : "Unhealthy") : "Not Configured"}
                  </p>
                  <p className="text-sm text-text-muted">
                    {selected.configured
                      ? `Last sync: ${selected.lastSync} · Latency: ${selected.latency}ms`
                      : "Click to configure this integration"}
                  </p>
                </div>
                {selected.configured && selected.healthy && (
                  <Badge variant="success">Operational</Badge>
                )}
                {selected.configured && !selected.healthy && (
                  <Badge variant="danger">Degraded</Badge>
                )}
                {!selected.configured && (
                  <Badge variant="outline">Not Connected</Badge>
                )}
              </div>

              {/* Description */}
              <div>
                <h4 className="mb-2 text-sm font-semibold text-text-secondary">Description</h4>
                <p className="text-sm text-text-muted">{selected.description}</p>
              </div>

              {/* Metrics */}
              {selected.metrics && Object.keys(selected.metrics).length > 0 && (
                <div>
                  <h4 className="mb-3 text-sm font-semibold text-text-secondary">Live Metrics</h4>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {Object.entries(selected.metrics).map(([key, value]) => (
                      <div key={key} className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                        <p className="text-xs font-medium text-text-muted">{key}</p>
                        <p className="mt-1 mono text-sm font-semibold text-text-primary">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Config */}
              {selected.config && Object.keys(selected.config).length > 0 && (
                <div>
                  <h4 className="mb-3 text-sm font-semibold text-text-secondary">Configuration</h4>
                  <div className="rounded-lg border border-border-default bg-white/[0.02] p-3">
                    <pre className="text-xs text-text-muted overflow-auto max-h-40">
                      {JSON.stringify(selected.config, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 border-t border-border-subtle pt-4">
                {selected.docsUrl && (
                  <a
                    href={selected.docsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 rounded-lg border border-border-default bg-white/[0.03] px-4 py-2 text-sm font-medium text-text-secondary hover:bg-white/[0.05] transition-colors"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Documentation
                  </a>
                )}
                <button className="rounded-lg bg-accent/20 px-4 py-2 text-sm font-semibold text-accent-light transition-colors hover:bg-accent/30">
                  {selected.configured ? "Reconfigure" : "Configure"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function IntegrationCard({ integration, selected, onClick }: { integration: typeof INTEGRATIONS[0]; selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "relative rounded-xl border p-5 transition-all duration-200 hover:shadow-lg",
        selected
          ? "border-accent/40 bg-accent/[0.03] shadow-[0_0_0_1px_theme(colors.accent)]"
          : "border-border-default bg-white/[0.02] hover:border-border-strong",
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={cn(
            "flex h-10 w-10 items-center justify-center rounded-lg",
            integration.configured && integration.healthy && "bg-status-low/15",
            integration.configured && !integration.healthy && "bg-status-critical/15",
            !integration.configured && "bg-text-muted/15",
          )}>
            {integration.icon}
          </div>
          <div>
            <h3 className="font-semibold text-text-primary">{integration.name}</h3>
            <p className="text-xs text-text-muted">{integration.category}</p>
          </div>
        </div>
        <div className={cn(
          "flex h-6 w-6 items-center justify-center rounded-full",
          integration.configured && integration.healthy && "bg-status-low/15 text-status-low",
          integration.configured && !integration.healthy && "bg-status-critical/15 text-status-critical",
          !integration.configured && "bg-text-muted/15 text-text-muted",
        )}>
          {integration.configured && integration.healthy && <CheckCircle2 className="h-3.5 w-3.5" />}
          {integration.configured && !integration.healthy && <XCircle className="h-3.5 w-3.5" />}
          {!integration.configured && <AlertCircle className="h-2.5 w-2.5" />}
        </div>
      </div>

      <p className="mt-3 text-sm text-text-muted line-clamp-2">{integration.description}</p>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs">
          {integration.latency && (
            <span className="flex items-center gap-1 text-text-muted">
              <Activity className="h-3 w-3" />
              {integration.latency}ms
            </span>
          )}
          {integration.requestsToday && (
            <span className="flex items-center gap-1 text-text-muted">
              <Zap className="h-3 w-3" />
              {integration.requestsToday.toLocaleString()}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {integration.configured && integration.healthy && (
            <Badge variant="success" className="text-[10px]">Healthy</Badge>
          )}
          {integration.configured && !integration.healthy && (
            <Badge variant="danger" className="text-[10px]">Degraded</Badge>
          )}
          {!integration.configured && (
            <Badge variant="outline" className="text-[10px]">Not Connected</Badge>
          )}
        </div>
      </div>

      {integration.lastSync && (
        <div className="mt-3 pt-3 border-t border-border-subtle flex items-center justify-between text-[10px] text-text-muted">
          <span>Last sync: {integration.lastSync}</span>
          {integration.version && <span className="mono">{integration.version}</span>}
        </div>
      )}
    </button>
  )
}