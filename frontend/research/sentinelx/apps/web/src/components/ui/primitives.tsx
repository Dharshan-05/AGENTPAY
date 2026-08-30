"use client"

import { cn } from "@/lib/utils"
import { Shield } from "lucide-react"
import { SEVERITY_BG, SEVERITY_COLORS } from "@/lib/api"

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode
  variant?: "default" | "outline" | "success" | "warning" | "danger" | "info"
  className?: string
}) {
  const variants = {
    default: "bg-white/[0.04] text-text-secondary border-border-default",
    outline: "bg-transparent text-text-secondary border-border-strong",
    success: "bg-low text-status-low border-status-low/20",
    warning: "bg-medium text-status-medium border-status-medium/20",
    danger: "bg-critical text-status-critical border-status-critical/20",
    info: "bg-info text-status-info border-status-info/20",
  }
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider",
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider", SEVERITY_BG[severity] ?? "bg-white/[0.03]", SEVERITY_COLORS[severity])}>
      <span className="h-1 w-1 rounded-full bg-current" />
      {severity.toLowerCase()}
    </span>
  )
}

export function DecisionBadge({ decision }: { decision: string }) {
  const color =
    decision === "BLOCK"
      ? "text-status-critical bg-critical"
      : decision === "REWRITE"
        ? "text-status-high bg-high"
        : decision === "FLAG"
          ? "text-status-medium bg-medium"
          : "text-status-low bg-low"
  return (
    <span className={cn("inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider", color)}>
      {decision}
    </span>
  )
}

export function RiskGauge({ score, size = "md" }: { score: number; size?: "sm" | "md" | "lg" }) {
  const color =
    score >= 80 ? "text-status-critical" : score >= 60 ? "text-status-high" : score >= 35 ? "text-status-medium" : "text-status-low"
  const dims = size === "lg" ? "h-24 w-24" : size === "sm" ? "h-14 w-14" : "h-20 w-20"
  const text = size === "lg" ? "text-3xl" : size === "sm" ? "text-lg" : "text-2xl"

  return (
    <div className={cn("relative flex items-center justify-center", dims)}>
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
        <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle
          cx="50"
          cy="50"
          r="42"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * 264} 264`}
          className={cn("transition-all duration-1000 ease-out", color)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn("mono font-bold", text, color)}>{Math.round(score)}</span>
        {size !== "sm" && <span className="text-[9px] uppercase tracking-widest text-text-muted">risk</span>}
      </div>
    </div>
  )
}

export function PageHeader({ title, description, actions }: { title: string; description?: string; actions?: React.ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-text-primary">{title}</h1>
        {description && <p className="mt-1 max-w-2xl text-sm text-text-secondary">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}

export function EmptyState({ title, description, icon: Icon }: { title: string; description?: string; icon?: React.ComponentType<{ className?: string }> }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border-strong py-16 text-center">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-white/[0.03]">
        {Icon ? <Icon className="h-6 w-6 text-text-muted" /> : <Shield className="h-6 w-6 text-text-muted" />}
      </div>
      <p className="text-sm font-medium text-text-primary">{title}</p>
      {description && <p className="mt-1 max-w-sm text-xs text-text-muted">{description}</p>}
    </div>
  )
}

export function SectionTitle({ title, sub, right }: { title: string; sub?: string; right?: React.ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <div>
        <h2 className="text-sm font-semibold text-text-primary">{title}</h2>
        {sub && <p className="text-[11px] text-text-muted">{sub}</p>}
      </div>
      {right}
    </div>
  )
}
