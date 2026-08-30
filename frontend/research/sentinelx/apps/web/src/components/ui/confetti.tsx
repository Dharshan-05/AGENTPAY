"use client"

import { useMemo } from "react"
import { motion } from "framer-motion"

const COLORS = ["#22c55e", "#0ea79c", "#0b827a", "#3b82f6", "#eab308", "#a855f7"]

export function Confetti({ count = 80 }: { count?: number }) {
  const pieces = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        delay: Math.random() * 0.6,
        duration: 2.2 + Math.random() * 1.6,
        rotation: Math.random() * 360,
        size: 6 + Math.random() * 6,
        color: COLORS[i % COLORS.length],
        round: Math.random() > 0.5,
      })),
    [count],
  )

  return (
    <div className="pointer-events-none fixed inset-0 z-[70] overflow-hidden" aria-hidden>
      {pieces.map((p) => (
        <motion.span
          key={p.id}
          initial={{ x: `${p.x}vw`, y: -20, rotate: 0, opacity: 1 }}
          animate={{ y: "105vh", rotate: p.rotation * 6, opacity: [1, 1, 0.6] }}
          transition={{ duration: p.duration, delay: p.delay, ease: "easeIn" }}
          className="absolute"
          style={{
            left: 0,
            width: p.size,
            height: p.round ? p.size : p.size * 0.45,
            background: p.color,
            borderRadius: p.round ? "50%" : 2,
            boxShadow: `0 0 6px ${p.color}88`,
          }}
        />
      ))}
    </div>
  )
}
