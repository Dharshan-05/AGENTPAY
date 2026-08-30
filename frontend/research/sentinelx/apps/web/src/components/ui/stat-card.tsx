"use client"

import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface StatCardProps {
  label: string
  value: React.ReactNode
  sub?: string
  icon: LucideIcon
  trend?: string
  trendUp?: boolean
  accent?: string
}

export function StatCard({ label, value, sub, icon: Icon, trend, trendUp, accent = "text-accent-light" }: StatCardProps) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted">{label}</p>
          <p className="mono mt-1.5 text-2xl font-semibold text-text-primary">{value}</p>
          {sub && <p className="mt-1 text-[11px] text-text-muted">{sub}</p>}
        </div>
        <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg bg-white/[0.03]", accent)}>
          <Icon className="h-4.5 w-4.5" />
        </div>
      </div>
      {trend && (
        <div className={cn("mt-2 flex items-center gap-1 text-[11px] font-medium", trendUp ? "text-status-low" : "text-status-critical")}>
          <span>{trend}</span>
          <span className="text-text-muted">vs previous period</span>
        </div>
      )}
    </div>
  )
}
