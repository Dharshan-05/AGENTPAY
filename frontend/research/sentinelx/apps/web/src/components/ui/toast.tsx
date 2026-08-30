"use client"

import * as React from "react"
import { AnimatePresence, motion } from "framer-motion"
import { CheckCircle2, AlertTriangle, Info, ShieldAlert, X, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

type ToastKind = "success" | "error" | "warning" | "info" | "live"

interface ToastItem {
  id: number
  kind: ToastKind
  title: string
  desc?: string
  duration: number
}

interface ToastContextValue {
  toast: (t: { kind?: ToastKind; title: string; desc?: string; duration?: number }) => void
}

const ToastContext = React.createContext<ToastContextValue | null>(null)

export function useToast(): ToastContextValue {
  const ctx = React.useContext(ToastContext)
  if (ctx) return ctx
  // Safe fallback when rendered outside a provider (e.g. during SSR/prerender).
  return React.useMemo(
    () => ({
      toast: () => {
        // no-op outside the live tree
      },
    }),
    [],
  )
}

let toastSeq = 0

const KIND_META: Record<ToastKind, { icon: typeof Zap; ring: string; bar: string; color: string }> = {
  success: { icon: CheckCircle2, ring: "border-status-low/30", bar: "bg-status-low", color: "text-status-low" },
  error: { icon: ShieldAlert, ring: "border-status-critical/30", bar: "bg-status-critical", color: "text-status-critical" },
  warning: { icon: AlertTriangle, ring: "border-status-medium/30", bar: "bg-status-medium", color: "text-status-medium" },
  info: { icon: Info, ring: "border-accent/30", bar: "bg-accent", color: "text-accent-light" },
  live: { icon: Zap, ring: "border-accent/40", bar: "bg-gradient-to-r from-accent-dark via-accent to-accent-light", color: "text-accent-light" },
}

export function Toaster() {
  const [items, setItems] = React.useState<ToastItem[]>([])
  const timers = React.useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map())

  const dismiss = React.useCallback((id: number) => {
    setItems((prev) => prev.filter((t) => t.id !== id))
    const t = timers.current.get(id)
    if (t) {
      clearTimeout(t)
      timers.current.delete(id)
    }
  }, [])

  const toast = React.useCallback<ToastContextValue["toast"]>(
    ({ kind = "info", title, desc, duration = 4200 }) => {
      const id = ++toastSeq
      setItems((prev) => [...prev.slice(-4), { id, kind, title, desc, duration }])
      const t = setTimeout(() => dismiss(id), duration)
      timers.current.set(id, t)
    },
    [dismiss],
  )

  React.useEffect(() => {
    return () => {
      timers.current.forEach((t) => clearTimeout(t))
      timers.current.clear()
    }
  }, [])

  const value = React.useMemo(() => ({ toast }), [toast])

  return (
    <ToastContext.Provider value={value}>
      <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-[min(360px,calc(100vw-2rem))] flex-col gap-2.5">
        <AnimatePresence mode="popLayout">
          {items.map((t) => {
            const meta = KIND_META[t.kind]
            return (
              <motion.div
                key={t.id}
                layout
                initial={{ opacity: 0, x: 48, scale: 0.96 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 48, scale: 0.96 }}
                transition={{ type: "spring", stiffness: 380, damping: 30 }}
                className={cn(
                  "pointer-events-auto relative overflow-hidden rounded-xl border bg-[#131316]/95 p-3.5 shadow-2xl shadow-black/60 backdrop-blur-xl",
                  meta.ring,
                )}
              >
                <div className="flex items-start gap-3">
                  <motion.span
                    initial={{ scale: 0, rotate: -30 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: "spring", stiffness: 500, damping: 22, delay: 0.05 }}
                    className={cn("mt-0.5 flex-shrink-0", meta.color)}
                  >
                    <meta.icon className="h-4.5 w-4.5" />
                  </motion.span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-text-primary">{t.title}</p>
                    {t.desc && <p className="mt-0.5 text-[11px] leading-relaxed text-text-secondary">{t.desc}</p>}
                  </div>
                  <button
                    onClick={() => dismiss(t.id)}
                    aria-label="Dismiss notification"
                    className="flex-shrink-0 rounded-md p-0.5 text-text-muted transition-colors hover:bg-white/[0.06] hover:text-text-primary"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
                <motion.div
                  initial={{ width: "100%" }}
                  animate={{ width: "0%" }}
                  transition={{ duration: t.duration / 1000, ease: "linear" }}
                  className={cn("absolute bottom-0 left-0 h-0.5", meta.bar)}
                />
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}
