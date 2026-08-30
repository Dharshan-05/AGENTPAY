"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export function Magnetic({
  children,
  className,
  strength = 18,
}: {
  children: React.ReactNode
  className?: string
  strength?: number
}) {
  const ref = React.useRef<HTMLDivElement>(null)
  const [offset, setOffset] = React.useState({ x: 0, y: 0 })

  const onMove = (e: React.MouseEvent) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    setOffset({ x: (x / rect.width) * strength, y: (y / rect.height) * strength })
  }

  const onLeave = () => setOffset({ x: 0, y: 0 })

  return (
    <motion.div
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      className={cn("inline-block", className)}
      animate={{ x: offset.x, y: offset.y }}
      transition={{ type: "spring", stiffness: 350, damping: 18 }}
    >
      {children}
    </motion.div>
  )
}
