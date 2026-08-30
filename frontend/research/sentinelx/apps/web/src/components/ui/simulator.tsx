"use client"

import { useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { Gauge, ShieldAlert, ShieldCheck, SlidersHorizontal, TrendingDown, TrendingUp, Users, Radar, BellRing } from "lucide-react"
import { api } from "@/lib/api"
import type { DashboardStats } from "@/types"
import { Badge } from "./primitives"
import { cn } from "@/lib/utils"

const clamp = (v: number, lo = 0, hi = 100) => Math.max(lo, Math.min(hi, Math.round(v)))

interface SliderDef {
  key: "strictness" | "awareness" | "threatVolume" | "sensitivity"
  label: string
  icon: typeof Gauge
  value: number
  hint: string
}

export function RiskSimulator() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [strictness, setStrictness] = useState(65)
  const [awareness, setAwareness] = useState(70)
  const [threatVolume, setThreatVolume] = useState(50)
  const [sensitivity, setSensitivity] = useState(60)
  const [dragging, setDragging] = useState(false)

  useEffect(() => {
    api.dashboard().then(setStats).catch(() => setStats(null))
  }, [])

  const set = (key: SliderDef["key"], v: number) => {
    if (key === "strictness") setStrictness(v)
    else if (key === "awareness") setAwareness(v)
    else if (key === "threatVolume") setThreatVolume(v)
    else setSensitivity(v)
  }

  const computed = useMemo(() => {
    if (!stats) return null
    const f1 = (strictness - 65) / 65
    const f2 = (awareness - 70) / 30
    const f3 = (threatVolume - 50) / 50
    const f4 = (sensitivity - 60) / 40
    const total = Math.max(stats.totalPrompts, 1)
    const risk = clamp(stats.riskScore - f1 * 16 - f2 * 9 + f3 * 12)
    const blocked = Math.max(0, Math.round(stats.blockedPrompts + f1 * total * 0.18 + f4 * total * 0.08 + f3 * total * 0.06))
    const violations = Math.max(0, Math.round(stats.violations24h - f1 * Math.max(stats.violations24h, 6) * 0.4 - f2 * Math.max(stats.violations24h, 6) * 0.35 + f4 * Math.max(stats.violations24h, 6) * 0.3))
    const compliance = clamp(stats.complianceHealth + f1 * 14 + f2 * 6 - f3 * 5 - f4 * 2)
    const rewriteRate = clamp(38 + f1 * 34 + f4 * 18)
    const productivity = clamp(96 - f1 * 22 - f4 * 8 + f2 * 5 - f3 * 4)
    return {
      risk,
      blocked,
      violations,
      compliance,
      rewriteRate,
      productivity,
      posture: risk >= 60 ? "DEGRADED" : risk >= 35 ? "ELEVATED" : "STABLE",
      blockedDelta: blocked - stats.blockedPrompts,
      riskDelta: risk - stats.riskScore,
    }
  }, [stats, strictness, awareness, threatVolume, sensitivity])

  if (!stats || !computed) {
    return (
      <div className="glass-card card-glow p-5">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-accent-light" />
          <h3 className="text-sm font-semibold">Enterprise Risk Simulator</h3>
        </div>
        <p className="mt-3 text-[11px] text-text-muted">Loading live posture…</p>
      </div>
    )
  }

  const scenario = strictness < 45 ? "Permissive" : strictness < 60 ? "Standard" : strictness < 80 ? "Hardened" : "Maximum"

  const sliders: SliderDef[] = [
    { key: "strictness", label: "Policy strictness", icon: Gauge, value: strictness, hint: "Enforcement thresholds for sensitive categories" },
    { key: "awareness", label: "Employee awareness", icon: Users, value: awareness, hint: "Training & secure-paste adoption rate" },
    { key: "threatVolume", label: "Threat volume", icon: Radar, value: threatVolume, hint: "Incoming attack activity against the gateway" },
    { key: "sensitivity", label: "Prompt sensitivity", icon: BellRing, value: sensitivity, hint: "How aggressively detection agents flag borderline prompts" },
  ]

  return (
    <div className="glass-card card-glow p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-accent-light" />
          <h3 className="text-sm font-semibold">Enterprise Risk Simulator</h3>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={strictness >= 80 ? "danger" : strictness >= 60 ? "warning" : "success"}>{scenario}</Badge>
          <span className="mono text-xs font-semibold text-accent-light">live</span>
        </div>
      </div>

      <div className="rounded-xl border border-border-default bg-white/[0.02] p-4">
        <div className="mb-2 flex items-center justify-between text-[11px]">
          <span className="font-medium text-text-secondary">Scenario controls</span>
          <span className="text-text-muted">recalculates live</span>
        </div>
        <div className="space-y-3">
          {sliders.map((s) => (
            <div key={s.key}>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-[11px] text-text-secondary">
                  <s.icon className="h-3 w-3 text-accent-light" /> {s.label}
                </span>
                <span className="mono text-[10px] text-text-muted">{s.value}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={s.value}
                onChange={(e) => set(s.key, Number(e.target.value))}
                onPointerDown={() => setDragging(true)}
                onPointerUp={() => setDragging(false)}
                aria-label={s.label}
                className="mt-1.5 w-full accent-[#0ea79c]"
              />
              <p className="mt-0.5 text-[9px] text-text-muted">{s.hint}</p>
            </div>
          ))}
        </div>
        <p className="mt-3 flex items-center gap-1.5 text-[11px] text-text-secondary">
          <Gauge className={cn("h-3.5 w-3.5", computed.riskDelta < 0 ? "text-status-low" : "text-status-high")} />
          {computed.riskDelta === 0 && computed.blockedDelta === 0
            ? "Current production posture — no changes applied."
            : computed.riskDelta < 0
              ? `This scenario lowers residual risk by ${Math.abs(computed.riskDelta)} pts while blocking ${computed.blockedDelta} more prompts.`
              : `This scenario raises residual risk by ${Math.abs(computed.riskDelta)} pts and reduces friction by ${Math.abs(computed.blockedDelta)} blocks.`}
        </p>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
        {[
          { label: "Residual risk", value: computed.risk, suffix: "/100", icon: TrendingDown, tone: computed.risk >= 60 ? "text-status-critical" : computed.risk >= 35 ? "text-status-high" : "text-status-low", sub: computed.riskDelta !== 0 ? `${computed.riskDelta > 0 ? "+" : ""}${computed.riskDelta}` : "unchanged" },
          { label: "Blocked prompts", value: computed.blocked, suffix: "", icon: ShieldAlert, tone: "text-status-critical", sub: computed.blockedDelta !== 0 ? `${computed.blockedDelta > 0 ? "+" : ""}${computed.blockedDelta}` : "unchanged" },
          { label: "Violations (24h)", value: computed.violations, suffix: "", icon: ShieldAlert, tone: computed.violations > 8 ? "text-status-high" : "text-status-medium", sub: "projected" },
          { label: "Compliance health", value: computed.compliance, suffix: "%", icon: ShieldCheck, tone: "text-status-low", sub: computed.compliance >= stats.complianceHealth ? "improving" : "declining" },
          { label: "Rewrite rate", value: computed.rewriteRate, suffix: "%", icon: Gauge, tone: "text-accent-light", sub: "of risky prompts" },
          { label: "Productivity", value: computed.productivity, suffix: "%", icon: TrendingUp, tone: computed.productivity >= 85 ? "text-status-low" : "text-status-medium", sub: "team friction" },
        ].map((m) => (
          <motion.div
            key={m.label}
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="rounded-lg border border-border-default bg-white/[0.02] p-3"
          >
            <div className="flex items-center justify-between">
              <m.icon className={cn("h-3.5 w-3.5", m.tone)} />
              <span className="text-[9px] text-text-muted">{m.sub}</span>
            </div>
            <motion.p
              key={m.value}
              initial={{ opacity: 0.4, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.25 }}
              className={cn("mono mt-1.5 text-lg font-semibold", m.tone)}
            >
              {m.value}{m.suffix}
            </motion.p>
            <p className="text-[9px] uppercase tracking-wider text-text-muted">{m.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between rounded-lg border border-accent/20 bg-accent/[0.04] px-3 py-2.5">
        <span className="text-[11px] text-text-secondary">Posture under this scenario</span>
        <span className={cn("mono text-sm font-bold", computed.risk >= 60 ? "text-status-critical" : computed.risk >= 35 ? "text-status-medium" : "text-status-low")}>
          {computed.posture}
        </span>
      </div>
      {dragging && <p className="mt-2 text-center text-[10px] text-accent-light animate-pulse">recalculating posture live…</p>}
    </div>
  )
}
