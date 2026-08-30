"use client"

import posthog from "posthog-js"

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com"

let initialized = false

export function initPostHog(): void {
  if (typeof window === "undefined" || initialized) return

  if (POSTHOG_KEY) {
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      autocapture: true,
      capture_pageview: true,
      capture_pageleave: true,
      persistence: "localStorage",
      loaded: (ph) => {
        if (process.env.NODE_ENV === "development") {
          ph.debug()
        }
      },
    })
    initialized = true
    console.log("[PostHog] Web initialized")
  } else {
    console.log("[PostHog] Web not configured — running in demo mode")
  }
}

export function isPostHogInitialized(): boolean {
  return initialized && !!POSTHOG_KEY
}

export function capture(event: string, properties?: Record<string, any>): void {
  if (!initialized || !POSTHOG_KEY) {
    console.log("[PostHog] Demo mode - event:", event, properties)
    return
  }

  try {
    posthog.capture(event, properties)
  } catch (error) {
    console.error("[PostHog] Capture failed:", error)
  }
}

export function identify(userId: string, traits?: Record<string, any>): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.identify(userId, traits)
  } catch (error) {
    console.error("[PostHog] Identify failed:", error)
  }
}

export function alias(userId: string): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.alias(userId)
  } catch (error) {
    console.error("[PostHog] Alias failed:", error)
  }
}

export function group(groupType: string, groupKey: string, properties?: Record<string, any>): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.group(groupType, groupKey, properties)
  } catch (error) {
    console.error("[PostHog] Group failed:", error)
  }
}

export function reset(): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.reset()
  } catch (error) {
    console.error("[PostHog] Reset failed:", error)
  }
}

export function register(property: string, value: any): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.register({ [property]: value })
  } catch (error) {
    console.error("[PostHog] Register failed:", error)
  }
}

export function unregister(property: string): void {
  if (!initialized || !POSTHOG_KEY) return

  try {
    posthog.unregister(property)
  } catch (error) {
    console.error("[PostHog] Unregister failed:", error)
  }
}

export function getDistinctId(): string | undefined {
  if (!initialized || !POSTHOG_KEY) return undefined
  return posthog.get_distinct_id()
}

export function healthCheck(): { initialized: boolean; configured: boolean } {
  return { initialized, configured: !!POSTHOG_KEY }
}

// Event types (mirror API side)
export const EVENTS = {
  LOGIN: "login",
  LOGOUT: "logout",
  PROMPT_SUBMITTED: "prompt_submitted",
  PROMPT_BLOCKED: "prompt_blocked",
  PROMPT_ALLOWED: "prompt_allowed",
  PROMPT_REWRITTEN: "prompt_rewritten",
  POLICY_TRIGGERED: "policy_triggered",
  SECRET_DETECTED: "secret_detected",
  INCIDENT_CREATED: "incident_created",
  INCIDENT_UPDATED: "incident_updated",
  INCIDENT_CLOSED: "incident_closed",
  INCIDENT_ASSIGNED: "incident_assigned",
  REPORT_GENERATED: "report_generated",
  REPORT_DOWNLOADED: "report_downloaded",
  DASHBOARD_VIEWED: "dashboard_viewed",
  EXECUTIVE_DASHBOARD_VIEWED: "executive_dashboard_viewed",
  COMPLIANCE_VIEWED: "compliance_viewed",
  COPILOT_USED: "copilot_used",
  COPILOT_SUGGESTION_CLICKED: "copilot_suggestion_clicked",
  SETTINGS_CHANGED: "settings_changed",
  PLAN_UPGRADED: "plan_upgraded",
  PAYMENT_COMPLETED: "payment_completed",
  PAYMENT_FAILED: "payment_failed",
  SUBSCRIPTION_CREATED: "subscription_created",
  SUBSCRIPTION_CANCELLED: "subscription_cancelled",
  NOTIFICATION_SENT: "notification_sent",
  SLACK_DELIVERED: "slack_delivered",
  EMAIL_DELIVERED: "email_delivered",
  FEATURE_USED: "feature_used",
  SEARCH_USED: "search_used",
  EXPORT_USED: "export_used",
  JUDGE_MODE_USED: "judge_mode_used",
} as const

export type EventName = typeof EVENTS[keyof typeof EVENTS]