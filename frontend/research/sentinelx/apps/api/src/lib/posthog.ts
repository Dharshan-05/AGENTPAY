import { PostHog } from "posthog-node"

const POSTHOG_API_KEY = process.env.POSTHOG_API_KEY
const POSTHOG_HOST = process.env.POSTHOG_HOST || "https://us.i.posthog.com"

let posthog: PostHog | null = null
let configured = false

if (POSTHOG_API_KEY) {
  posthog = new PostHog(POSTHOG_API_KEY, {
    host: POSTHOG_HOST,
    flushAt: 20,
    flushInterval: 10000,
  })
  configured = true
  console.log("[PostHog] Configured")
} else {
  console.log("[PostHog] Not configured — running in demo mode")
}

export interface AnalyticsEvent {
  event: string
  distinctId: string
  properties?: Record<string, any>
  timestamp?: Date
}

export function isPostHogConfigured(): boolean {
  return configured
}

export function getPostHogClient(): PostHog | null {
  return posthog
}

export async function capture(event: AnalyticsEvent): Promise<boolean> {
  if (!configured || !posthog) {
    console.log("[PostHog] Demo mode - event:", event.event, event.properties)
    return true
  }

  try {
    posthog.capture({
      distinctId: event.distinctId,
      event: event.event,
      properties: event.properties,
      timestamp: event.timestamp,
    })
    return true
  } catch (error) {
    console.error("[PostHog] Capture failed:", error)
    return false
  }
}

export async function identify(userId: string, traits: Record<string, any>): Promise<boolean> {
  if (!configured || !posthog) return true

  try {
    posthog.identify({
      distinctId: userId,
      properties: traits,
    })
    return true
  } catch (error) {
    console.error("[PostHog] Identify failed:", error)
    return false
  }
}

export async function group(groupId: string, properties: Record<string, any>): Promise<boolean> {
  if (!configured || !posthog) return true

  try {
    posthog.groupIdentify({
      groupType: "organization",
      groupKey: groupId,
      properties,
    })
    return true
  } catch (error) {
    console.error("[PostHog] Group identify failed:", error)
    return false
  }
}

export async function alias(previousId: string, newId: string): Promise<boolean> {
  if (!configured || !posthog) return true

  try {
    posthog.alias({ distinctId: newId, alias: previousId })
    return true
  } catch (error) {
    console.error("[PostHog] Alias failed:", error)
    return false
  }
}

export async function flush(): Promise<void> {
  if (!configured || !posthog) return

  try {
    await posthog.flush()
  } catch (error) {
    console.error("[PostHog] Flush failed:", error)
  }
}

export async function shutdown(): Promise<void> {
  if (!configured || !posthog) return

  try {
    await posthog.shutdown()
  } catch (error) {
    console.error("[PostHog] Shutdown failed:", error)
  }
}

export function healthCheck(): { configured: boolean; host?: string } {
  return { configured, host: configured ? POSTHOG_HOST : undefined }
}

// Event type constants
export const EVENTS = {
  // Auth
  LOGIN: "login",
  LOGOUT: "logout",
  
  // Prompt scanning
  PROMPT_SUBMITTED: "prompt_submitted",
  PROMPT_BLOCKED: "prompt_blocked",
  PROMPT_ALLOWED: "prompt_allowed",
  PROMPT_REWRITTEN: "prompt_rewritten",
  
  // Policy
  POLICY_TRIGGERED: "policy_triggered",
  SECRET_DETECTED: "secret_detected",
  
  // Incidents
  INCIDENT_CREATED: "incident_created",
  INCIDENT_UPDATED: "incident_updated",
  INCIDENT_CLOSED: "incident_closed",
  INCIDENT_ASSIGNED: "incident_assigned",
  
  // Reports
  REPORT_GENERATED: "report_generated",
  REPORT_DOWNLOADED: "report_downloaded",
  
  // Dashboard
  DASHBOARD_VIEWED: "dashboard_viewed",
  EXECUTIVE_DASHBOARD_VIEWED: "executive_dashboard_viewed",
  COMPLIANCE_VIEWED: "compliance_viewed",
  
  // Copilot
  COPILOT_USED: "copilot_used",
  COPILOT_SUGGESTION_CLICKED: "copilot_suggestion_clicked",
  
  // Settings
  SETTINGS_CHANGED: "settings_changed",
  PLAN_UPGRADED: "plan_upgraded",
  
  // Billing
  PAYMENT_COMPLETED: "payment_completed",
  PAYMENT_FAILED: "payment_failed",
  SUBSCRIPTION_CREATED: "subscription_created",
  SUBSCRIPTION_CANCELLED: "subscription_cancelled",
  
  // Notifications
  NOTIFICATION_SENT: "notification_sent",
  SLACK_DELIVERED: "slack_delivered",
  EMAIL_DELIVERED: "email_delivered",
  
  // Feature usage
  FEATURE_USED: "feature_used",
  SEARCH_USED: "search_used",
  EXPORT_USED: "export_used",
  JUDGE_MODE_USED: "judge_mode_used",
} as const

export type EventName = typeof EVENTS[keyof typeof EVENTS]