"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import * as SwitchPrimitive from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"

export function CountUp({
  value,
  duration = 1.2,
  className,
  decimals = 0,
  suffix = "",
  format,
}: {
  value: number
  duration?: number
  className?: string
  decimals?: number
  suffix?: string
  format?: (v: number) => string
}) {
  const [display, setDisplay] = useState(0)
  const prev = useRef(0)

  useEffect(() => {
    const start = prev.current
    const target = value
    if (Math.abs(start - target) < 10 ** -decimals) {
      prev.current = target
      return
    }
    const startTime = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - startTime) / (duration * 1000))
      const eased = 1 - Math.pow(1 - t, 3)
      const next = start + (target - start) * eased
      setDisplay(next)
      if (t < 1) raf = requestAnimationFrame(tick)
      else prev.current = target
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      prev.current = target
    }
  }, [value, duration, decimals])

  if (format) return <span className={className}>{format(display)}</span>
  return <span className={className}>{display.toLocaleString(undefined, { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}{suffix}</span>
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton", className)} />
}

export function GlowCard({
  children,
  className,
  danger = false,
  delay = 0,
}: {
  children: React.ReactNode
  className?: string
  danger?: boolean
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={cn("glass-card card-glow", danger && "card-glow-danger", className)}
    >
      {children}
    </motion.div>
  )
}

export function Switch({
  checked,
  onCheckedChange,
  disabled,
  label,
}: {
  checked: boolean
  onCheckedChange: (v: boolean) => void
  disabled?: boolean
  label?: string
}) {
  return (
    <SwitchPrimitive.Root
      checked={checked}
      onCheckedChange={onCheckedChange}
      disabled={disabled}
      aria-label={label}
      className={cn(
        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border transition-colors outline-none",
        "focus-visible:ring-2 focus-visible:ring-accent/40",
        checked ? "border-accent/60 bg-accent/40" : "border-border-strong bg-white/[0.04]",
        disabled && "cursor-not-allowed opacity-40",
      )}
    >
      <SwitchPrimitive.Thumb
        className={cn(
          "block h-3.5 w-3.5 rounded-full shadow transition-transform",
          checked ? "translate-x-[18px] bg-accent-light" : "translate-x-[2px] bg-text-muted",
        )}
      />
    </SwitchPrimitive.Root>
  )
}
