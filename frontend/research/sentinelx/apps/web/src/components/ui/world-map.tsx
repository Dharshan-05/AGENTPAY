"use client"

import { motion } from "framer-motion"
import { memo, useMemo } from "react"
import type { SocStats } from "@/types"

function project(lat: number, lng: number, width: number, height: number): [number, number] {
  const x = ((lng + 180) / 360) * width
  const y = ((90 - lat) / 180) * height
  return [x, y]
}

const SEVERITY_RING: Record<string, string> = {
  CRITICAL: "#ef4444",
  HIGH: "#f97316",
  MEDIUM: "#eab308",
  LOW: "#22c55e",
  SAFE: "#22c55e",
}

export const WorldThreatMap = memo(function WorldThreatMap({ data }: { data: SocStats["threatMap"] }) {
  const width = 800
  const height = 400
  const dots = useMemo(() => data.map((e) => ({ ...e, x: project(e.lat, e.lng, width, height)[0], y: project(e.lat, e.lng, width, height)[1] })), [data, width, height])

  const gridLines = []
  for (let i = 0; i <= 8; i++) gridLines.push({ x: (width / 8) * i })
  for (let j = 0; j <= 4; j++) gridLines.push({ y: (height / 4) * j })

  return (
    <div className="relative overflow-hidden rounded-xl border border-border-default bg-gradient-to-br from-white/[0.01] to-transparent">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label="Simulated global threat map">
        <defs>
          <radialGradient id="mapGlow" cx="50%" cy="45%" r="60%">
            <stop offset="0%" stopColor="rgba(11,130,122,0.05)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>
        <rect width={width} height={height} fill="url(#mapGlow)" />
        {gridLines.map((l, i) => (
          l.x !== undefined ? (
            <line key={`v${i}`} x1={l.x} y1={0} x2={l.x} y2={height} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          ) : (
            <line key={`h${i}`} x1={0} y1={l.y} x2={width} y2={l.y} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          )
        ))}
        {gridLines.filter((l) => l.x !== undefined).map((l, i) => (
          <line key={`vx${i}`} x1={l.x} y1={0} x2={l.x} y2={height} stroke="rgba(11,130,122,0.03)" strokeWidth="1" strokeDasharray="2 6" />
        ))}
        {dots.map((e, i) => {
          const color = SEVERITY_RING[e.severity] ?? "#22c55e"
          return (
            <g key={e.id}>
              <motion.circle
                cx={e.x}
                cy={e.y}
                r={4 + e.count * 1.5}
                fill={color}
                fillOpacity={0.25}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.08 }}
              />
              <motion.circle
                cx={e.x}
                cy={e.y}
                r={2.5}
                fill={color}
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.6, 1, 0.6] }}
                transition={{ delay: i * 0.08, duration: 2.4, repeat: Infinity }}
              />
              <motion.ellipse
                cx={e.x}
                cy={e.y}
                rx={6 + e.count * 2}
                ry={3 + e.count}
                fill={color}
                opacity={0.35}
                initial={{ opacity: 0 }}
                animate={{ opacity: [0, 0.45, 0] }}
                transition={{ delay: i * 0.08, duration: 3, repeat: Infinity }}
              />
            </g>
          )
        })}
      </svg>
      <div className="pointer-events-none absolute bottom-2 left-2 flex gap-3">
        {Object.entries(SEVERITY_RING).slice(0, 4).map(([k, c]) => (
          <span key={k} className="flex items-center gap-1 text-[9px] uppercase tracking-wider text-text-muted">
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: c }} /> {k.toLowerCase()}
          </span>
        ))}
      </div>
    </div>
  )
})
