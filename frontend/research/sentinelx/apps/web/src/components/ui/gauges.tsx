"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export function MaturityGauge({ score, label }: { score: number; label: string }) {
  const color = score >= 85 ? "text-status-low" : score >= 65 ? "text-status-info" : score >= 45 ? "text-status-medium" : "text-status-critical"
  return (
    <div className="flex flex-col items-center">
      <div className="relative h-36 w-36">
        <svg viewBox="0 0 120 120" className="h-full w-full">
          <path
            d="M 15 105 A 52 52 0 1 1 105 105"
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="11"
            strokeLinecap="round"
          />
          <motion.path
            d="M 15 105 A 52 52 0 1 1 105 105"
            fill="none"
            stroke="currentColor"
            strokeWidth="11"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: score / 100 }}
            transition={{ duration: 1.4, ease: "easeOut" }}
            className={color}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("mono text-3xl font-bold", color)}>{score}</span>
          <span className="text-[9px] uppercase tracking-widest text-text-muted">of 100</span>
        </div>
      </div>
      <p className="mt-3 text-center text-xs font-semibold text-text-primary">{label}</p>
    </div>
  )
}

export function ScoreRing({ value, size = 140, stroke = 10, className }: { value: number; size?: number; stroke?: number; className?: string }) {
  const color = value >= 85 ? "#22c55e" : value >= 70 ? "#0ea79c" : value >= 50 ? "#eab308" : "#ef4444"
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  return (
    <div className={cn("relative flex items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={stroke} />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c * (1 - value / 100) }}
          transition={{ duration: 1.4, ease: "easeOut" }}
          style={{ filter: `drop-shadow(0 0 8px ${color}55)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="mono text-3xl font-bold" style={{ color }}>{Math.round(value)}</span>
        <span className="text-[9px] uppercase tracking-widest text-text-muted">score</span>
      </div>
    </div>
  )
}
