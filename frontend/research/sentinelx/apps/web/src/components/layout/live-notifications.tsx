"use client"

import { useEffect } from "react"
import { subscribeIncidentNew } from "@/lib/live"
import { useToast } from "@/components/ui/toast"

export function LiveNotifications() {
  const { toast } = useToast()

  useEffect(() => {
    const off = subscribeIncidentNew((inc) => {
      toast({
        kind: "live",
        title: `New ${inc.severity} incident — ${inc.id}`,
        desc: `${inc.title} · ${inc.department} · risk ${inc.riskScore}/100`,
      })
    })
    return off
  }, [toast])

  return null
}
