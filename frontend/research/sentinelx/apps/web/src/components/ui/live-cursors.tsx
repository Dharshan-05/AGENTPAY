"use client"

import { motion } from "framer-motion"

interface CursorDef {
  name: string
  role: string
  color: string
  paths: Array<[number, number]>
}

const CURSORS: CursorDef[] = [
  { name: "Aarav Mehta", role: "SOC Lead", color: "#0ea79c", paths: [[8, 22], [44, 58], [76, 26], [52, 80], [20, 40]] },
  { name: "Priya Sharma", role: "Incident Commander", color: "#3b82f6", paths: [[72, 14], [38, 70], [14, 34], [66, 82], [84, 48]] },
  { name: "Daniel Okafor", role: "Threat Hunter", color: "#f97316", paths: [[28, 82], [64, 18], [88, 62], [24, 26], [58, 90]] },
  { name: "Sofia Reyes", role: "Compliance", color: "#a855f7", paths: [[88, 78], [52, 30], [12, 66], [70, 12], [34, 54]] },
  { name: "Kenji Watanabe", role: "Cloud Sec", color: "#22c55e", paths: [[44, 88], [80, 40], [26, 12], [60, 66], [92, 20]] },
]

function Cursor({ c, delay }: { c: CursorDef; delay: number }) {
  const xs = c.paths.map((p) => `${p[0]}%`)
  const ys = c.paths.map((p) => `${p[1]}%`)
  return (
    <motion.div
      className="pointer-events-none absolute left-0 top-0 z-20"
      initial={{ x: xs[0], y: ys[0], opacity: 0 }}
      animate={{ x: xs, y: ys, opacity: 1 }}
      transition={{ duration: 16, repeat: Infinity, ease: "easeInOut", delay, times: c.paths.map((_, i) => i / (c.paths.length - 1)) }}
    >
      <div className="relative flex flex-col items-center">
        <span
          className="absolute -top-7 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md border border-white/10 bg-black/80 px-2 py-0.5 text-[9px] font-medium text-white backdrop-blur"
        >
          {c.name} <span className="opacity-60">· {c.role}</span>
        </span>
        <svg width="17" height="17" viewBox="0 0 24 24" style={{ filter: `drop-shadow(0 0 6px ${c.color}88)` }}>
          <path d="M4 2l7 18 2.4-7.6L21 10z" fill={c.color} />
          <path d="M4 2l7 18 2.4-7.6L21 10z" fill="none" stroke="white" strokeWidth="0.8" strokeOpacity="0.4" />
        </svg>
      </div>
    </motion.div>
  )
}

export function LiveCursorLayer({ className }: { className?: string }) {
  return (
    <div className={className}>
      <div className="pointer-events-none absolute inset-0 z-10 overflow-visible">
        {CURSORS.map((c, i) => (
          <Cursor key={c.name} c={c} delay={i * 2.6} />
        ))}
      </div>
    </div>
  )
}
